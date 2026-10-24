"""Deterministic, explicitly labeled recorded-evidence replay. Never a live agent claim."""
import json
from pathlib import Path

from .models import Institution, ResearchRequest, Source, Fact, Extraction, Hypothesis


def fixture():
    return json.loads((Path(__file__).resolve().parent.parent / "data" / "demo.json").read_text(encoding="utf-8"))


def demo_request():
    data = fixture()
    return ResearchRequest(home=Institution(**data["home"]), market=data["market"])


class DemoSearch:
    mode = "recorded"

    def __init__(self, outage=False):
        self.data = fixture()
        self.outage = outage

    def search(self, query, domain=None):
        if domain == "skylacu.com" and self.outage:
            raise TimeoutError("Simulated unavailable source")
        sources = [Source(**s) for s in self.data["sources"]]
        return [s for s in sources if not domain or domain in s.url]


class DemoAnalyst:
    mode = "recorded"

    def __init__(self):
        self.data = fixture()

    def discover(self, request, sources):
        if request["home"]["domain"] != "truliantfcu.org" or request["market"] != self.data["market"]:
            raise ValueError("Recorded demo supports only Truliant in Charlotte. Use live mode for another scope.")
        return [Institution(**x) for x in self.data["competitors"]]

    def extract(self, institution, sources):
        source = next((s for s in sources if institution.domain in s.url), None)
        facts = {k:Fact(**v, source_id=source.id) for k,v in self.data["facts"].get(institution.domain, {}).items()} if source else {}
        return Extraction(facts=facts, follow_up="checking membership eligibility acquisition offer conditions")

    def analyze(self, request, profiles):
        available = sorted({f["source_id"] for p in profiles for f in p["facts"].values() if f["status"] == "Source-supported"})
        if not available:
            return []
        def refs(*ids):
            return [i for i in ids if i in available] or available[:1]
        return [
            Hypothesis(title="Make the path to a waived monthly fee easy to understand", rationale="The collected checking pages present fees alongside qualifying conditions. Clearer explanations may reduce uncertainty during account selection; these excerpts do not establish which institution is cheapest for every customer.", source_ids=refs("demo-truliant", "demo-truist", "demo-bofa"), experiment="Compare the current checking landing page with a plain-language fee-and-waiver explanation. Use only terms approved by the product owner.", success_metric="Compare application-start rate and completed funded-account rate between variants; also monitor misunderstanding-related support contacts.", caveat="Hypothesis, not measured uplift. Review all waiver alternatives and current disclosures before testing."),
            Hypothesis(title="Test an opening-deposit explanation in the switching journey", rationale="Recorded product pages describe opening funding requirements. Explaining opening funding separately from ongoing balance requirements may help prospective members complete an application.", source_ids=refs("demo-truliant", "demo-truist", "demo-skyla"), experiment="Add a short opening-funding checklist before the application handoff; compare against the existing journey.", success_metric="Measure funded accounts per completed application and abandonment at the funding step.", caveat="No evidence here identifies the actual cause of abandonment. Validate the journey with users and confirm membership eligibility."),
            Hypothesis(title="Test total-value messaging alongside fee transparency", rationale="The collected pages show different checking terms and conditions. Test whether an audience-specific explanation of approved benefits improves acquisition quality rather than assuming a lower headline fee wins.", source_ids=refs("demo-truliant", "demo-skyla", "demo-truist"), experiment="Interview prospects, then compare approved benefit-led and fee-led messaging with the same offer and audience.", success_metric="Measure funded-account conversion and subsequent primary-account activation; define activation before the test.", caveat="These excerpts do not establish feature superiority, customer preferences, campaign economics or expected growth.")
        ]
