import unittest
from growth.usage import event, price_tokens, summarize


class CacheCostTests(unittest.TestCase):
    def test_http_response_preserves_lifetime_details_before_parsing_failure(self):
        import httpx
        from unittest.mock import patch
        from langchain_openai import ChatOpenAI
        from pydantic import BaseModel
        from growth.providers import LiveAnalyst
        class Result(BaseModel):
            ready: bool
        def handler(request):
            return httpx.Response(200,json={'id':'test','object':'chat.completion','created':1,'model':'gpt-6-luna','service_tier':'default','choices':[{'index':0,'message':{'role':'assistant','content':'not json'},'finish_reason':'stop'}], 'usage':{'prompt_tokens':12000,'completion_tokens':200,'total_tokens':12200,'prompt_tokens_details':{'cached_tokens':4000,'cache_write_tokens':7000,'cache_write_tokens_details':{'ttl_30m_tokens':3000,'ttl_12h_tokens':4000}},'completion_tokens_details':{'reasoning_tokens':100}}})
        client=httpx.Client(transport=httpx.MockTransport(handler))
        def factory(**kwargs):
            return ChatOpenAI(http_client=client,**kwargs)
        with patch('growth.providers.ChatOpenAI',side_effect=factory):
            analyst=LiveAnalyst('test-key','gpt-6-luna')
            with self.assertRaises(ValueError):
                analyst._json(Result,'Return ready',{})
        r=analyst.events[0]
        self.assertEqual(r['cache_write_12h_tokens'],4000)
        self.assertEqual(r['outcome'],'failed')
        self.assertAlmostEqual(r['total_cost_usd'],(1000*.10+4000*.01+3000*.125+4000*.25+200*.5)/1e6)

    def record(self, details, raw=None, tier='default'):
        record=event('OpenAI','gpt-6-luna')
        metadata={'service_tier':tier}
        if raw is not None:
            metadata['token_usage']={'prompt_tokens_details':raw}
        price_tokens(record,{'input_tokens':12000,'output_tokens':200,'total_tokens':12200,'input_token_details':details,'output_token_details':{'reasoning':100}},metadata)
        return record

    def test_implicit_cache_writes_replace_ordinary_input_charge(self):
        r=self.record({'cache_read':4000,'cache_creation':7000})
        self.assertEqual(r.get('cache_write_tokens'),7000)
        self.assertEqual(r.get('ordinary_input_tokens'),1000)
        self.assertAlmostEqual(r.get('input_cost_usd') or 0,(1000*.10+4000*.01+7000*.125)/1e6)
        self.assertAlmostEqual(r.get('total_cost_usd') or 0,(1000*.10+4000*.01+7000*.125+200*.5)/1e6)
        self.assertEqual(r.get('cache_write_lifetime_basis'),'Default 30m; app sends no lifetime overrides')

    def test_mixed_lifetimes_use_raw_provider_breakdown(self):
        r=self.record({'cache_read':4000,'cache_creation':7000},{'cached_tokens':4000,'cache_write_tokens':7000,'cache_write_tokens_details':{'ttl_30m_tokens':3000,'ttl_12h_tokens':4000}})
        self.assertAlmostEqual(r.get('cache_write_cost_usd') or 0,(3000*.125+4000*.25)/1e6)
        self.assertAlmostEqual(r.get('input_cost_usd') or 0,(1000*.10+4000*.01+3000*.125+4000*.25)/1e6)

    def test_inconsistent_lifetime_breakdown_stays_unpriced(self):
        r=self.record({'cache_read':4000,'cache_creation':7000},{'cache_write_tokens':7000,'cache_write_tokens_details':{'ttl_30m_tokens':3000,'ttl_12h_tokens':3000}})
        self.assertIsNone(r['total_cost_usd'])
        self.assertIn('lifetime',r.get('pricing_status',''))

    def test_invalid_partitions_and_unknown_tier_stay_unpriced(self):
        for details,tier in [({'cache_read':8000,'cache_creation':7000},'default'),({'cache_read':0,'cache_creation':-1},'default'),({'cache_read':0,'cache_creation':0},'priority')]:
            with self.subTest(details=details,tier=tier):
                r=self.record(details,tier=tier)
                self.assertIsNone(r['total_cost_usd'])

    def test_absent_write_count_is_unknown_and_output_still_priced(self):
        r=self.record({'cache_read':0})
        self.assertIsNone(r.get('cache_write_tokens'))
        self.assertIsNone(r['input_cost_usd'])
        self.assertAlmostEqual(r['output_cost_usd'],200*.5/1e6)

    def test_summary_keeps_write_cost_inside_input_total(self):
        r=self.record({'cache_read':4000,'cache_creation':7000})
        s=summarize([r,r])
        self.assertEqual(s.get('cache_write_tokens'),14000)
        self.assertAlmostEqual(s['total_cost_usd'],2*(r['input_cost_usd']+r['output_cost_usd']))
        self.assertEqual(s['unpriced_calls'],0)


if __name__=='__main__':
    unittest.main()
