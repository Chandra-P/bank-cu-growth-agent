import unittest
from growth.planning import ProposalInputs, calculate_proposal, target_alignment, proposal_default_target
from growth.demo import DemoSearch, DemoAnalyst, demo_request
from growth.graph import build_graph, new_state
from growth.report import export_bundle
from langgraph.types import Command


class TargetAlignmentTests(unittest.TestCase):
    def result(self, outcome='Funded checking accounts', target=300):
        return {'request':{'client_discovery':{'target_accounts':target, 'target_outcome':outcome}}, 'proposal':calculate_proposal(ProposalInputs(target_accounts=300))}

    def test_structured_target_defaults_and_mismatch(self):
        result = self.result()
        self.assertEqual(proposal_default_target(result),300)
        self.assertEqual(target_alignment(result)['status'],'matched')
        result['proposal'] = calculate_proposal(ProposalInputs(target_accounts=500))
        self.assertEqual(target_alignment(result)['status'],'mismatch')

    def test_incompatible_and_unknown_targets_are_not_called_matched(self):
        self.assertEqual(target_alignment(self.result('Opened accounts'))['status'],'incompatible')
        self.assertEqual(target_alignment(self.result('Not specified',None))['status'],'assumption')
        self.assertEqual(target_alignment(self.result('Not specified'))['status'],'assumption')

    def test_unknown_target_cannot_approve_without_explicit_review(self):
        from growth.planning import save_proposal
        graph = build_graph(DemoSearch(),DemoAnalyst())
        config={'configurable':{'thread_id':self.id()},'recursion_limit':60}
        result=graph.invoke(new_state(demo_request(),'recorded'),config)
        result=graph.invoke(Command(resume={'competitors':result['candidates']}),config)
        save_proposal(graph,config,result,ProposalInputs())
        result=graph.invoke(Command(resume={'approve':True,'note':'Missing target review'}),config)
        self.assertEqual(result['__interrupt__'][0].value['stage'],'review')
        self.assertFalse(graph.get_state(config).values['approved'])
        result=graph.invoke(Command(resume={'approve':True,'note':'Explicitly reviewed planning assumption','target_alignment_confirmed':True}),config)
        self.assertTrue(result['approved'])

    def test_matched_target_approval_and_export_receipt(self):
        from growth.planning import save_proposal
        from growth.models import ResearchRequest
        graph=build_graph(DemoSearch(),DemoAnalyst())
        request=ResearchRequest(**{**demo_request().model_dump(),'client_discovery':{}})
        config={'configurable':{'thread_id':self.id()},'recursion_limit':60}
        result=graph.invoke(new_state(request,'recorded'),config)
        result=graph.invoke(Command(resume={'competitors':result['candidates']}),config)
        discovery=dict(goal='300 funded accounts',timeframe='Next quarter',target_accounts=300,target_outcome='Funded checking accounts',problem='Account funding',observation='Illustrative client-reported funding drop-off; validate data.',success_definition='Unique funded accounts with $100 within 30 days',confirmed=True)
        result=graph.invoke(Command(resume=discovery),config)
        with self.assertRaises(ValueError):
            save_proposal(graph,config,result,ProposalInputs(target_accounts=500))
        result=save_proposal(graph,config,result,ProposalInputs(target_accounts=300))
        result=graph.invoke(Command(resume={'approve':True,'note':'Matched target reviewed'}),config)
        md,raw=export_bundle(result)
        self.assertIn('300 funded checking accounts',md)
        self.assertEqual(result['approval']['target_alignment']['status'],'matched')

    def test_export_rechecks_target_after_approval(self):
        result=self.result()
        result.update(approved=True,status='approved',run_id='test',approval={'approved':True,'run_id':'test'})
        result['proposal']=calculate_proposal(ProposalInputs(target_accounts=500))
        with self.assertRaises(PermissionError):
            export_bundle(result)
