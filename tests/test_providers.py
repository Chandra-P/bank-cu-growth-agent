import unittest
import httpx
from unittest.mock import patch
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from growth.providers import bounded_call, ProviderError, TavilySearch, LiveAnalyst


class ProviderTests(unittest.TestCase):
    def test_reasoning_model_request_avoids_unsupported_temperature(self):
        import json
        class Result(BaseModel):
            ready: bool
        def handler(request):
            payload = json.loads(request.content)
            if "temperature" in payload:
                return httpx.Response(400,json={"error":{"message":"Unsupported temperature", "type":"invalid_request_error", "param":"temperature", "code":"unsupported_value"}})
            return httpx.Response(200,json={"id":"chat-test","object":"chat.completion","created":1,"model":"gpt-6-luna","choices":[{"index":0,"message":{"role":"assistant","content":"{\"ready\": true}"},"finish_reason":"stop"}],"usage":{"prompt_tokens":10,"completion_tokens":5,"total_tokens":15}})
        client = httpx.Client(transport=httpx.MockTransport(handler))
        def model_factory(**kwargs):
            return ChatOpenAI(http_client=client,**kwargs)
        # The shipped .env leaves OPENAI_BASE_URL empty for the default provider.
        with patch.dict("os.environ", {"OPENAI_BASE_URL":""}), patch("growth.providers.ChatOpenAI",side_effect=model_factory):
            result = LiveAnalyst("test-key","gpt-6-luna")._json(Result,"Return ready true",{})
        self.assertTrue(result.ready)

    def test_transient_failure_retries_once_and_recovers(self):
        calls = []
        events = []
        def call():
            calls.append(1)
            if len(calls) == 1:
                raise TimeoutError("secret-key-must-not-be-logged")
            return "recovered"
        self.assertEqual(bounded_call(call, "search", events, delay=0), "recovered")
        self.assertEqual(len(calls), 2)
        self.assertNotIn("secret-key", str(events))

    def test_permanent_failure_stops_after_two_attempts_without_secrets(self):
        calls = []
        events = []
        def fail():
            calls.append(1)
            raise RuntimeError("sensitive-provider-response")
        with self.assertRaises(ProviderError):
            bounded_call(fail, "model", events, delay=0)
        self.assertEqual(len(calls), 2)
        self.assertNotIn("sensitive-provider-response", str(events))

    def test_tavily_scopes_queries_and_filters_unsafe_results(self):
        requests = []
        def handler(request):
            import json
            requests.append(json.loads(request.content))
            return httpx.Response(200, json={"results": [
                {"url":"https://example.com/checking", "title":"Checking", "content":"Monthly fee $0"},
                {"url":"javascript:alert(1)", "title":"Bad", "content":"Bad"},
                {"url":"https://example.com.evil.org/", "title":"Wrong", "content":"Bad"}]})
        client = httpx.Client(transport=httpx.MockTransport(handler))
        results = TavilySearch("test-key", client=client).search("checking", "example.com")
        self.assertEqual(len(results), 1)
        self.assertEqual(requests[0]["include_domains"], ["example.com"])
        self.assertEqual(requests[0]["max_results"], 5)
        self.assertEqual(results[0].url, "https://example.com/checking")

    def test_malformed_search_result_fails_cleanly(self):
        client = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"unexpected":[]})))
        with self.assertRaises(ValueError):
            TavilySearch("test-key", client=client).search("checking")

    def test_tavily_preserves_full_page_terms_when_snippet_omits_them(self):
        def handler(request):
            return httpx.Response(200,json={"results":[{"url":"https://example.com/checking","title":"Example Checking","content":"No monthly fee.","raw_content":"No monthly fee with enrollment in electronic statements."}]})
        client=httpx.Client(transport=httpx.MockTransport(handler))
        source=TavilySearch("test-key",client=client).search("checking","example.com")[0]
        self.assertIn("with enrollment in electronic statements",source.excerpt)
        self.assertIn("Example Checking",source.excerpt)
