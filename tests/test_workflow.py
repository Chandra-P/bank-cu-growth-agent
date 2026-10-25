import json
import unittest

from langgraph.types import Command

from growth.demo import DemoSearch, DemoAnalyst, demo_request
from growth.graph import build_graph, new_state
from growth.report import export_bundle


class WorkflowTests(unittest.TestCase):
    def start(self, outage=False):
        graph = build_graph(DemoSearch(outage=outage), DemoAnalyst())
        config = {"configurable": {"thread_id": self.id()}, "recursion_limit": 60}
        result = graph.invoke(new_state(demo_request(), "recorded"), config)
        return graph, config, result

    def research(self, graph, config, result):
        return graph.invoke(Command(resume={"competitors": result["candidates"]}), config)

    def test_graph_pauses_before_research_and_before_export(self):
        graph, config, result = self.start()
        self.assertEqual(result["__interrupt__"][0].value["stage"], "competitors")
        self.assertEqual(result["profiles"], [])
        with self.assertRaises(PermissionError):
            export_bundle(result)
        result = self.research(graph, config, result)
        self.assertEqual(result["__interrupt__"][0].value["stage"], "review")
        self.assertEqual(len(result["profiles"]), 4)
        self.assertEqual(len(result["hypotheses"]), 3)
        self.assertFalse(result["approved"])
        with self.assertRaises(PermissionError):
            export_bundle(result)
        result = graph.invoke(Command(resume={"approve": True, "note": "Reviewed sources"}), config)
        md, js = export_bundle(result)
        self.assertIn("RECORDED", md)
        self.assertIn("Charlotte", md)
        self.assertIn("Not verified", md)
        self.assertIn("bankofamerica.com", md)
        self.assertEqual(json.loads(js)["approval"]["note"], "Reviewed sources")

    def test_outage_finishes_with_unknowns_and_bounded_attempts(self):
        graph, config, result = self.start(outage=True)
        result = self.research(graph, config, result)
        unavailable = next(p for p in result["profiles"] if p["institution"]["domain"] == "skylacu.com")
        self.assertTrue(all(f["status"] == "Not verified" for f in unavailable["facts"].values()))
        failures = [e for e in result["trace"] if e.get("action") == "search:skylacu.com:1"]
        self.assertEqual([e["attempt"] for e in failures], [1, 2])
        self.assertEqual(len(result["profiles"]), 4)
        self.assertIn("review", str(result["__interrupt__"]))

    def test_rejection_does_not_allow_export(self):
        graph, config, result = self.start()
        result = self.research(graph, config, result)
        result = graph.invoke(Command(resume={"approve": False, "note": "Need better evidence"}), config)
        self.assertEqual(result["status"], "rejected")
        with self.assertRaises(PermissionError):
            export_bundle(result)

    def test_follow_up_extraction_outage_preserves_supported_first_round(self):
        class FollowUpOutage(DemoAnalyst):
            def __init__(self):
                super().__init__()
                self.calls = {}
            def extract(self, institution, sources):
                self.calls[institution.domain] = self.calls.get(institution.domain, 0) + 1
                if institution.domain == 'truliantfcu.org' and self.calls[institution.domain] > 1:
                    raise RuntimeError('Simulated follow-up outage')
                return super().extract(institution, sources)
        analyst = FollowUpOutage()
        graph = build_graph(DemoSearch(), analyst)
        config = {'configurable': {'thread_id': self.id()}, 'recursion_limit': 60}
        result = graph.invoke(new_state(demo_request(), 'recorded'), config)
        result = self.research(graph, config, result)
        home = result['profiles'][0]
        self.assertEqual(home['facts']['product_name']['status'], 'Source-supported')
        self.assertGreater(sum(f['status'] == 'Source-supported' for f in home['facts'].values()), 0)
        self.assertTrue(any('retained' in w for w in result['warnings']))
        self.assertFalse(result['approved'])

    def test_recorded_mode_rejects_a_different_market(self):
        request = demo_request().model_copy(update={"market": "Seattle, WA"})
        graph = build_graph(DemoSearch(), DemoAnalyst())
        with self.assertRaises(ValueError):
            graph.invoke(new_state(request, "recorded"), {"configurable":{"thread_id":"bad-scope"}})

    def test_follow_up_search_is_bounded_to_two_rounds(self):
        graph, config, result = self.start()
        result = self.research(graph, config, result)
        searches = [e for e in result["trace"] if e.get("action", "").startswith("search:") and e.get("outcome") == "ok"]
        self.assertLessEqual(len(searches), 8)
        self.assertTrue(any(e["action"].endswith(":2") for e in searches))

    def test_forged_hypothesis_sources_are_removed(self):
        from growth.models import Hypothesis
        class BadAnalyst(DemoAnalyst):
            def analyze(self, request, profiles):
                return [Hypothesis(title="Invented", rationale="Unsupported", source_ids=["fake"], experiment="Test", success_metric="Measure", caveat="Unknown")]
        graph = build_graph(DemoSearch(), BadAnalyst())
        config = {"configurable":{"thread_id":"forged"},"recursion_limit":60}
        result = graph.invoke(new_state(demo_request(), "recorded"), config)
        result = graph.invoke(Command(resume={"competitors":result["candidates"]}), config)
        self.assertEqual(result["hypotheses"], [])
        self.assertTrue(result["warnings"])

    def test_unidentified_product_cannot_supply_comparison_terms(self):
        from growth.models import Fact
        class MissingProductAnalyst(DemoAnalyst):
            def extract(self,institution,sources):
                result=super().extract(institution,sources)
                if institution.domain == "skylacu.com":
                    result.facts["product_name"]=Fact()
                return result
        graph=build_graph(DemoSearch(),MissingProductAnalyst())
        config={"configurable":{"thread_id":"missing-product"},"recursion_limit":60}
        result=graph.invoke(new_state(demo_request(),"recorded"),config)
        result=graph.invoke(Command(resume={"competitors":result["candidates"]}),config)
        skyla=next(p for p in result["profiles"] if p["institution"]["domain"] == "skylacu.com")
        self.assertTrue(all(f["status"] == "Not verified" for f in skyla["facts"].values()))
        self.assertTrue(any("product identity" in w.lower() for w in result["warnings"]))
