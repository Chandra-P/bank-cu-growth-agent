import json
import unittest
from decimal import Decimal
from langgraph.types import Command
from growth.demo import DemoSearch, DemoAnalyst, demo_request
from growth.graph import build_graph, new_state
from growth.planning import ProposalInputs, calculate_proposal, save_proposal
from growth.report import export_bundle


class PlanningTests(unittest.TestCase):
    def test_default_range_and_all_in_envelopes(self):
        plan = calculate_proposal(ProposalInputs())
        base = plan['scenarios'][1]
        self.assertEqual(base['total_usd'], '225000.00')
        self.assertEqual(base['direct_mail_usd'], '157500.00')
        self.assertEqual(base['display_usd'], '67500.00')
        self.assertEqual(base['paid_social_usd'], '0.00')
        self.assertEqual([r['total_usd'] for r in plan['scenarios']], ['150000.00', '225000.00', '300000.00'])

    def test_paid_social_and_overrides(self):
        plan = calculate_proposal(ProposalInputs(include_paid_social=True, direct_mail_pct=60, display_pct=25, paid_social_pct=15))
        self.assertEqual(plan['scenarios'][1]['paid_social_usd'], '33750.00')
        plan = calculate_proposal(ProposalInputs(target_accounts=300, cpa_low=350, cpa_base=400, cpa_high=500, direct_mail_pct=80, display_pct=20))
        self.assertEqual(plan['scenarios'][1]['total_usd'], '120000.00')

    def test_invalid_inputs_rejected(self):
        for kwargs in ({'target_accounts':0}, {'cpa_low':600}, {'direct_mail_pct':90}, {'paid_social_pct':10}, {'include_paid_social':True}, {'cpa_low':'NaN'}, {'cpa_base':'0.001'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                ProposalInputs(**kwargs)

    def test_allocations_reconcile_to_the_cent(self):
        plan = calculate_proposal(ProposalInputs(target_accounts=1, cpa_low='.01', cpa_base='.01', cpa_high='.01', include_paid_social=True, direct_mail_pct=60, display_pct=25, paid_social_pct=15))
        for row in plan['scenarios']:
            self.assertEqual(sum(Decimal(row[k]) for k in ('direct_mail_usd','display_usd','paid_social_usd')), Decimal(row['total_usd']))

    def test_save_preserves_review_and_exports_only_after_approval(self):
        graph = build_graph(DemoSearch(), DemoAnalyst())
        config = {'configurable':{'thread_id':self.id()}, 'recursion_limit':60}
        result = graph.invoke(new_state(demo_request(), 'recorded'), config)
        result = graph.invoke(Command(resume={'competitors':result['candidates']}), config)
        result = save_proposal(graph, config, result, ProposalInputs())
        self.assertEqual(result['proposal']['scenarios'][1]['total_usd'], '225000.00')
        self.assertFalse(result['approved'])
        with self.assertRaises(PermissionError):
            export_bundle(result)
        result = graph.invoke(Command(resume={'approve':True,'note':'Reviewed assumptions'}), config)
        md, raw = export_bundle(result)
        self.assertIn('225,000.00', md)
        self.assertEqual(json.loads(raw)['proposal']['assumption_source'], 'Strategist-provided planning assumptions; not verified performance benchmarks')
        with self.assertRaises(ValueError):
            save_proposal(graph, config, result, ProposalInputs())

    def test_discovery_needed_cannot_save_budget(self):
        with self.assertRaises(ValueError):
            save_proposal(None, None, {'status':'awaiting review','decision':'discovery needed'}, ProposalInputs())
