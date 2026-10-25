import unittest
from langgraph.types import Command
from growth.demo import DemoAnalyst, DemoSearch, demo_request
from growth.graph import build_graph, new_state


class DiscoveryCheckpointTests(unittest.TestCase):
    def start(self):
        request = demo_request().model_dump()
        request['client_discovery'] = {}
        graph = build_graph(DemoSearch(), DemoAnalyst())
        config = {'configurable': {'thread_id': self.id()}, 'recursion_limit': 60}
        from growth.models import ResearchRequest
        result = graph.invoke(new_state(ResearchRequest(**request), 'recorded'), config)
        result = graph.invoke(Command(resume={'competitors': result['candidates']}), config)
        return graph, config, result

    def ready(self):
        return dict(goal='More funded checking accounts', timeframe='Next quarter',
                    problem='Account funding', observation='Illustrative client-reported funnel: completed applications are not funding; validate counts.',
                    success_definition='Unique new checking accounts funded with at least $100 within 30 days; exclude duplicates.',
                    constraints='Budget and reachable audiences not yet agreed.', confirmed=True)

    def test_checkpoint_preserves_research_and_waits_for_strategist(self):
        _, _, result = self.start()
        self.assertEqual(result['status'], 'awaiting discovery')
        self.assertEqual(result['__interrupt__'][0].value['stage'], 'discovery')
        self.assertEqual(len(result['profiles']), 4)
        self.assertFalse(result['hypotheses'])

    def test_live_run_always_requires_checkpoint_even_without_discovery_input(self):
        search, analyst = DemoSearch(), DemoAnalyst()
        search.mode = analyst.mode = 'live'
        graph = build_graph(search, analyst)
        config = {'configurable': {'thread_id': self.id()}, 'recursion_limit': 60}
        result = graph.invoke(new_state(demo_request(), 'live'), config)
        result = graph.invoke(Command(resume={'competitors': result['candidates']}), config)
        self.assertEqual(result['status'], 'awaiting discovery')
        self.assertEqual(result['__interrupt__'][0].value['stage'], 'discovery')
        self.assertFalse(result['hypotheses'])

    def test_unknown_problem_withholds_campaigns_and_can_refine_without_research(self):
        graph, config, result = self.start()
        answer = self.ready()
        answer['problem'] = 'Unknown / needs discovery'
        result = graph.invoke(Command(resume=answer), config)
        self.assertEqual(result['decision'], 'discovery needed')
        self.assertTrue(result['discovery_questions'])
        self.assertFalse(result['hypotheses'])
        self.assertEqual(result['revision_count'], 0)
        self.assertFalse(any(e.get('action') == 'analysis:agent' for e in result['trace']))
        research_calls = len([e for e in result['trace'] if e.get('action', '').startswith('search:')])
        graph.update_state(config, {'status': 'awaiting discovery'}, as_node='save_profile')
        result = graph.invoke(None, config)
        self.assertEqual(result['__interrupt__'][0].value['stage'], 'discovery')
        result = graph.invoke(Command(resume=self.ready()), config)
        self.assertEqual(result['decision'], 'campaign planning ready')
        self.assertEqual(len(result['hypotheses']), 3)
        self.assertEqual(research_calls, len([e for e in result['trace'] if e.get('action', '').startswith('search:')]))
        self.assertFalse(result['approved'])

    def test_confirmation_does_not_bypass_missing_evidence(self):
        graph, config, _ = self.start()
        answer = self.ready()
        answer['observation'] = ' '
        result = graph.invoke(Command(resume=answer), config)
        self.assertEqual(result['decision'], 'discovery needed')
        self.assertFalse(result['hypotheses'])

    def test_explicit_unknown_fields_do_not_start_paid_campaign_work(self):
        graph, config, _ = self.start()
        answer = self.ready()
        for field in ('goal', 'timeframe', 'observation', 'success_definition'):
            answer[field] = 'Unknown / needs discovery'
        result = graph.invoke(Command(resume=answer), config)
        self.assertEqual(result['decision'], 'discovery needed')
        self.assertFalse(result['hypotheses'])
        self.assertFalse(any(e.get('action') in ('analysis:agent', 'benchmarks:search', 'strategy:revision') for e in result['trace']))

    def test_unconfirmed_discovery_export_does_not_claim_confirmation(self):
        graph, config, _ = self.start()
        answer = self.ready()
        answer['confirmed'] = False
        result = graph.invoke(Command(resume=answer), config)
        result = graph.invoke(Command(resume={'approve': True, 'note': 'Evidence-only discovery brief'}), config)
        from growth.report import export_bundle
        md, _ = export_bundle(result)
        self.assertIn('**Strategist confirmation:** Not confirmed', md)
        self.assertNotIn('## Strategist-confirmed discovery', md)
        self.assertIn('Campaign concepts withheld', md)

    def test_client_discovery_survives_approved_export(self):
        graph, config, _ = self.start()
        result = graph.invoke(Command(resume=self.ready()), config)
        result = graph.invoke(Command(resume={'approve': True, 'note': 'Recorded scenario review'}), config)
        from growth.report import export_bundle
        import json
        md, raw = export_bundle(result)
        self.assertIn('Account funding', md)
        self.assertEqual(json.loads(raw)['decision'], 'campaign planning ready')
