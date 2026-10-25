import json
import unittest

from langgraph.types import Command
from pydantic import ValidationError

from growth.demo import DemoAnalyst, DemoSearch, demo_request
from growth.graph import build_graph, new_state
from growth.models import Hypothesis, ResearchRequest
from growth.report import export_bundle


class StrategyTests(unittest.TestCase):
    def run_brief(self, analyst=None, brief=""):
        request = ResearchRequest(**{**demo_request().model_dump(), "client_brief": brief})
        graph = build_graph(DemoSearch(), analyst or DemoAnalyst())
        config = {"configurable": {"thread_id": self.id()}, "recursion_limit": 60}
        result = graph.invoke(new_state(request, "recorded"), config)
        result = graph.invoke(Command(resume={"competitors": result["candidates"]}), config)
        return graph, config, result

    def test_client_brief_campaigns_and_takeaway_survive_approved_export(self):
        brief = "Annual goal: more funded checking relationships. Problem: application abandonment."
        graph, config, result = self.run_brief(brief=brief)
        self.assertEqual(result["request"]["client_brief"], brief)
        takeaway = result["strategist_takeaway"]
        self.assertTrue(takeaway["finding"])
        self.assertTrue(takeaway["client_question"])
        supported = {f["source_id"] for p in result["profiles"] for f in p["facts"].values() if f["status"] == "Source-supported"}
        self.assertTrue(set(takeaway["source_ids"]).issubset(supported))
        for campaign in result["hypotheses"]:
            for field in ["audience", "need_connection", "message", "channel_rationale", "guardrail", "client_question"]:
                self.assertTrue(campaign[field], field)
            self.assertTrue(campaign["channels"])
            self.assertTrue(set(campaign["channels"]).issubset({"Direct mail", "Display", "Paid social"}))
        with self.assertRaises(PermissionError):
            export_bundle(result)
        result = graph.invoke(Command(resume={"approve": True, "note": "Reviewed draft concepts"}), config)
        md, raw = export_bundle(result)
        self.assertIn("Strategist takeaway", md)
        self.assertIn(brief, md)
        self.assertIn("Client validation question", md)
        self.assertIn("Paid social", md)
        self.assertEqual(json.loads(raw)["strategist_takeaway"], takeaway)

    def test_campaign_rejects_unapproved_channels(self):
        with self.assertRaises(ValidationError):
            Hypothesis(title="Test", rationale="Reason", source_ids=["s1"], experiment="Test", success_metric="Measure", caveat="Unknown", channels=["Email"])

    def test_client_brief_is_bounded(self):
        with self.assertRaises(ValidationError):
            ResearchRequest(**{**demo_request().model_dump(), "client_brief": "x" * 2001})

    def test_forged_takeaway_citations_are_withheld(self):
        from growth.models import StrategistTakeaway
        class BadTakeaway(DemoAnalyst):
            def analyze(self, request, profiles):
                result = super().analyze(request, profiles)
                result.takeaway = StrategistTakeaway(finding="Invented", implication="Invented", client_question="Validate?", source_ids=["fake-source"])
                return result
        _, _, result = self.run_brief(BadTakeaway())
        self.assertIsNone(result["strategist_takeaway"])
        self.assertTrue(any("takeaway" in w.lower() for w in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
