import unittest
import httpx

from growth.providers import bounded_call, ProviderError, TavilySearch


class ProviderTests(unittest.TestCase):
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
