import unittest
from unittest.mock import patch
from pathlib import Path

from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def open(self):
        return AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()

    def test_client_context_and_campaign_brief_are_visible_before_approval(self):
        app = self.open()
        app.text_area(key="client_brief").set_value("Client goal: funded checking accounts; confirm abandonment cause.")
        app.button(key="start_research").click().run()
        app.button(key="confirm_competitors").click().run()
        self.assertFalse(app.exception)
        self.assertIn("funded checking", app.session_state["result"]["request"]["client_brief"])
        headings = [h.value for h in app.subheader]
        self.assertIn("Strategist takeaway", headings)
        self.assertIn("Campaign concepts for the client discussion", headings)
        self.assertIn('Agent activity & AI costs', headings)
        self.assertIn('Review & revision', headings)
        self.assertIn('Public acquisition benchmarks', headings)
        self.assertEqual(app.session_state['result']['revision_count'],1)
        self.assertFalse(app.get("download_button"))
        self.assertTrue(app.button(key="approve_report").disabled)

    def test_live_usage_panel_discloses_unknown_costs(self):
        app=self.open()
        app.button(key='start_research').click().run()
        app.button(key='confirm_competitors').click().run()
        result=dict(app.session_state['result'])
        result['mode']='live'
        result['usage']=[{'agent':'Strategy','provider':'OpenAI','action':'strategy:review','outcome':'failed','input_tokens':100,'output_tokens':20,'total_tokens':120,'input_cost_usd':None,'output_cost_usd':None,'total_cost_usd':None}]
        app.session_state['result']=result
        app.run()
        self.assertFalse(app.exception)
        self.assertTrue(any('1 have unknown cost' in w.value for w in app.warning))
        self.assertTrue(app.button(key='approve_report').disabled)

    def test_live_never_uses_server_keys_and_requires_visitor_keys(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY":"server-openai-sentinel", "TAVILY_API_KEY":"server-tavily-sentinel"}):
            app = self.open()
            app.selectbox(key="mode").select("Live research").run()
            self.assertEqual(app.text_input(key="visitor_openai_key").value, "")
            self.assertEqual(app.text_input(key="visitor_tavily_key").value, "")
            self.assertTrue(app.button(key="start_research").disabled)
            app.text_input(key="visitor_openai_key").set_value("visitor-openai-sentinel").run()
            self.assertTrue(app.button(key="start_research").disabled)
            app.text_input(key="visitor_tavily_key").set_value("visitor-tavily-sentinel").run()
            self.assertFalse(app.button(key="start_research").disabled)
            other = self.open()
            other.selectbox(key="mode").select("Live research").run()
            self.assertEqual(other.text_input(key="visitor_openai_key").value, "")
            self.assertTrue(other.button(key="start_research").disabled)

    def test_clear_keys_also_discards_graph_and_report(self):
        app = self.open()
        app.text_input(key="visitor_openai_key").set_value("visitor-openai-sentinel").run()
        app.text_input(key="visitor_tavily_key").set_value("visitor-tavily-sentinel").run()
        app.button(key="start_research").click().run()
        self.assertIsNotNone(app.session_state["graph"])
        app.button(key="clear_keys").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.text_input(key="visitor_openai_key").value, "")
        self.assertEqual(app.text_input(key="visitor_tavily_key").value, "")
        self.assertIsNone(app.session_state["graph"])
        self.assertIsNone(app.session_state["config"])
        self.assertIsNone(app.session_state["result"])
        self.assertFalse(app.get("download_button"))

    def test_demo_requires_confirmation_and_approval_before_download(self):
        app = self.open()
        self.assertFalse(app.exception)
        self.assertFalse(app.get("download_button"))
        app.button(key="start_research").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["status"], "awaiting competitors")
        self.assertFalse(app.get("download_button"))
        app.button(key="confirm_competitors").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["status"], "awaiting review")
        self.assertFalse(app.get("download_button"))
        self.assertTrue(app.button(key="approve_report").disabled)
        app.checkbox(key="reviewed_evidence").check().run()
        app.button(key="approve_report").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("download_button")), 2)
        self.assertEqual(app.session_state["result"]["status"], "approved")

    def test_rejection_and_reset_remove_export_state(self):
        app = self.open()
        app.button(key="start_research").click().run()
        app.button(key="confirm_competitors").click().run()
        app.button(key="reject_report").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.get("download_button"))
        self.assertEqual(app.session_state["result"]["status"], "rejected")
        app.button(key="new_research").click().run()
        self.assertFalse(app.exception)
        self.assertIsNone(app.session_state["result"])

    def test_outage_is_visible_and_workflow_does_not_crash(self):
        app = self.open()
        # Form values are sent together with submit, matching browser behavior.
        app.checkbox(key="demo_outage").check()
        app.button(key="start_research").click().run()
        app.button(key="confirm_competitors").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.session_state["result"]["warnings"])
        self.assertEqual(len(app.session_state["result"]["profiles"]), 4)
