import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from pydantic import BaseModel
from langgraph.types import Command
from growth.providers import LiveAnalyst, bounded_call, ProviderError
from growth.demo import DemoSearch, DemoAnalyst, demo_request
from growth.graph import build_graph, new_state


class ObservabilityTests(unittest.TestCase):
    def test_source_quoted_funded_checking_cpa_is_retained(self):
        from growth.models import Benchmark, BenchmarkResearch, Source
        class AccountSearch(DemoSearch):
            def search(self, query, domain=None):
                if 'case study' in query:
                    return [Source(id='account-cost',title='Campaign',url='https://example.com/campaign',excerpt='Cost per funded checking account was $150. Costs include media only.',retrieved_at='2026-10-24')]
                return super().search(query,domain)
        class AccountBenchmark(DemoAnalyst):
            def benchmarks(self, request, sources):
                return BenchmarkResearch(benchmarks=[Benchmark(source_id='account-cost',quote=sources[0].excerpt,channel='Unspecified',cpa=150,product='Checking',account_definition='Funded checking account',geography_audience='Not specified',period='Not specified',costs_included='Media',costs_excluded='Not specified',comparability='Confirm audience and missing costs')],limitations='Case study is not a forecast.')
        graph=build_graph(AccountSearch(),AccountBenchmark())
        config={'configurable':{'thread_id':self.id()},'recursion_limit':60}
        result=graph.invoke(new_state(demo_request(),'recorded'),config)
        result=graph.invoke(Command(resume={'competitors':result['candidates']}),config)
        self.assertEqual(result['benchmarks']['benchmarks'][0]['cpa'],150)

    def test_omitted_cache_and_reasoning_breakdown_remain_unknown(self):
        from growth.usage import event, price_tokens
        record=event('OpenAI','gpt-6-luna')
        price_tokens(record, {'input_tokens':100,'output_tokens':20,'total_tokens':120}, {})
        self.assertIsNone(record['cached_input_tokens'])
        self.assertIsNone(record['reasoning_tokens'])
        self.assertIsNone(record['input_cost_usd'])
        self.assertAlmostEqual(record['output_cost_usd'],20*.5/1e6)
        self.assertIsNone(record['total_cost_usd'])
        from growth.usage import summarize
        self.assertAlmostEqual(summarize([record])['total_cost_usd'],record['output_cost_usd'])

    def test_lead_cost_cannot_be_relabelled_funded_checking_cpa(self):
        from growth.models import Benchmark, BenchmarkResearch, Source
        class LeadSearch(DemoSearch):
            def search(self, query, domain=None):
                if 'case study' in query:
                    return [Source(id='lead-cost',title='Campaign',url='https://example.com/campaign',excerpt='The checking campaign achieved a cost per lead of $25.',retrieved_at='2026-10-24')]
                return super().search(query,domain)
        class Relabelled(DemoAnalyst):
            def benchmarks(self, request, sources):
                return BenchmarkResearch(benchmarks=[Benchmark(source_id='lead-cost', quote=sources[0].excerpt, channel='Direct mail', cpa=25, product='Checking',account_definition='Funded checking account',geography_audience='Unknown',period='Unknown',costs_included='Not specified',costs_excluded='Not specified',comparability='Needs review')],limitations='Test')
        graph=build_graph(LeadSearch(),Relabelled())
        config={'configurable':{'thread_id':self.id()},'recursion_limit':60}
        result=graph.invoke(new_state(demo_request(),'recorded'),config)
        result=graph.invoke(Command(resume={'competitors':result['candidates']}),config)
        self.assertEqual(result['benchmarks']['benchmarks'],[])

    def run_demo(self, analyst):
        graph=build_graph(DemoSearch(), analyst)
        config={'configurable':{'thread_id':self.id()}, 'recursion_limit':60}
        result=graph.invoke(new_state(demo_request(), 'recorded'), config)
        return graph.invoke(Command(resume={'competitors':result['candidates']}), config)

    def test_failed_review_retains_original_and_still_requires_human(self):
        class FailedReview(DemoAnalyst):
            def critique(self, context):
                raise TimeoutError('private provider detail')
        result=self.run_demo(FailedReview())
        self.assertEqual(result['revision_count'],0)
        self.assertEqual(result['hypotheses'], result['draft_hypotheses'])
        self.assertFalse(result['approved'])
        self.assertNotIn('private provider detail', str(result))
        self.assertEqual(sum(e['action']=='strategy:review' for e in result['trace']),2)

    def test_unsupported_revision_is_rejected_entirely(self):
        class BadRevision(DemoAnalyst):
            def revise(self, context):
                result=super().revise(context)
                result.hypotheses[0].source_ids=['forged-source']
                return result
        result=self.run_demo(BadRevision())
        self.assertEqual(result['revision_count'],0)
        self.assertEqual(result['hypotheses'],result['draft_hypotheses'])
        self.assertTrue(any('Revision unavailable' in w for w in result['warnings']))

    def test_benchmark_amount_must_appear_in_source_quote(self):
        from growth.models import Benchmark, BenchmarkResearch
        class BadBenchmark(DemoAnalyst):
            def benchmarks(self, request, sources):
                s=sources[0]
                return BenchmarkResearch(benchmarks=[Benchmark(source_id=s.id, quote=s.excerpt[:200], channel='Direct mail', cpa=987654, product='Checking', account_definition='Funded account', geography_audience='Unknown', period='Unknown', costs_included='Not specified', costs_excluded='Not specified', comparability='Needs review')],limitations='Test')
        result=self.run_demo(BadBenchmark())
        self.assertEqual(result['benchmarks']['benchmarks'],[])
        self.assertTrue(any('CPA was withheld' in w for w in result['warnings']))

    def test_usage_captured_even_when_json_parse_fails(self):
        class Result(BaseModel):
            ready: bool
        analyst = LiveAnalyst('test-key', 'gpt-6-luna')
        analyst.model = Mock()
        analyst.model.invoke.return_value = SimpleNamespace(content='invalid json', usage_metadata={'input_tokens':100, 'output_tokens':20, 'total_tokens':120, 'input_token_details':{'cache_read':40}, 'output_token_details':{'reasoning':5}}, response_metadata={'model_name':'gpt-6-luna'})
        with self.assertRaises(ProviderError):
            bounded_call(lambda: analyst._json(Result, 'test', {}), 'analysis:agent', [], delay=0)
        self.assertEqual(len(analyst.events), 2)
        self.assertEqual(analyst.events[0]['input_tokens'], 100)
        self.assertEqual(analyst.events[0]['output_tokens'], 20)
        self.assertEqual(analyst.events[0]['cached_input_tokens'], 40)
        self.assertAlmostEqual(analyst.events[0]['input_cost_usd'], (60*.10 + 40*.01)/1e6)
        self.assertAlmostEqual(analyst.events[0]['output_cost_usd'], 20*.50/1e6)
        self.assertEqual(analyst.events[0]['outcome'], 'failed')

    def test_missing_usage_and_unknown_model_are_not_zero_cost(self):
        class Result(BaseModel):
            ready: bool
        analyst = LiveAnalyst('test-key', 'unknown-model')
        analyst.model = Mock()
        analyst.model.invoke.return_value = SimpleNamespace(content='{"ready":true}', usage_metadata=None, response_metadata={})
        analyst._json(Result, 'test', {})
        self.assertIsNone(analyst.events[0]['total_tokens'])
        self.assertIsNone(analyst.events[0]['total_cost_usd'])
        self.assertNotIn('test-key', str(analyst.events))

    def test_four_roles_review_and_one_revision_in_demo(self):
        graph=build_graph(DemoSearch(), DemoAnalyst())
        config={'configurable':{'thread_id':self.id()}, 'recursion_limit':60}
        result=graph.invoke(new_state(demo_request(), 'recorded'), config)
        result=graph.invoke(Command(resume={'competitors':result['candidates']}), config)
        self.assertEqual(result['status'], 'awaiting review')
        self.assertEqual(result['revision_count'], 1)
        self.assertTrue(result['review_findings'])
        self.assertTrue(result['draft_hypotheses'])
        self.assertIn('benchmarks:agent', [e['action'] for e in result['trace']])
        self.assertEqual(sum(e['action']=='strategy:revision' for e in result['trace']), 1)
        self.assertEqual(result['usage'], [])
        self.assertFalse(result['approved'])


if __name__=='__main__':
    unittest.main()
