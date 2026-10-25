"""Deterministic, explicitly labeled recorded-evidence replay. Never a live agent claim."""
import json
from pathlib import Path

from .models import Institution, ResearchRequest, Source, Fact, Extraction, Hypothesis, Analysis, StrategistTakeaway, BenchmarkResearch, RecommendationReview


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
        hypotheses = [
            Hypothesis(title="Make the path to a waived monthly fee easy to understand", rationale="The collected checking pages present fees alongside qualifying conditions. Clearer explanations may reduce uncertainty during account selection; these excerpts do not establish which institution is cheapest for every customer.", source_ids=refs("demo-truliant", "demo-truist", "demo-bofa"), experiment="Compare the current checking landing page with a plain-language fee-and-waiver explanation. Use only terms approved by the product owner.", success_metric="Compare application-start rate and completed funded-account rate between variants; also monitor misunderstanding-related support contacts.", caveat="Hypothesis, not measured uplift. Review all waiver alternatives and current disclosures before testing."),
            Hypothesis(title="Test an opening-deposit explanation in the switching journey", rationale="Recorded product pages describe opening funding requirements. Explaining opening funding separately from ongoing balance requirements may help prospective members complete an application.", source_ids=refs("demo-truliant", "demo-truist", "demo-skyla"), experiment="Add a short opening-funding checklist before the application handoff; compare against the existing journey.", success_metric="Measure funded accounts per completed application and abandonment at the funding step.", caveat="No evidence here identifies the actual cause of abandonment. Validate the journey with users and confirm membership eligibility."),
            Hypothesis(title="Test total-value messaging alongside fee transparency", rationale="The collected pages show different checking terms and conditions. Test whether an audience-specific explanation of approved benefits improves acquisition quality rather than assuming a lower headline fee wins.", source_ids=refs("demo-truliant", "demo-skyla", "demo-truist"), experiment="Interview prospects, then compare approved benefit-led and fee-led messaging with the same offer and audience.", success_metric="Measure funded-account conversion and subsequent primary-account activation; define activation before the test.", caveat="These excerpts do not establish feature superiority, customer preferences, campaign economics or expected growth.")
        ]
        for h, channels in zip(hypotheses, [['Direct mail', 'Display'], ['Paid social', 'Display'], ['Direct mail', 'Paid social']]):
            h.audience = 'Prospective eligible checking households in the confirmed market; audience availability to validate.'
            h.need_connection = 'Provisional funded-checking acquisition concept; confirm the client priority and actual journey problem.'
            h.message = 'Understand the checking account terms and the steps to getting started.'
            h.channels = channels
            roles = {'Direct mail':'Direct mail explains approved terms to an eligible prospect audience.', 'Display':'Display reinforces the message and links to the product journey.', 'Paid social':'Paid social tests approved creative and sends prospects to the checking page.'}
            h.channel_rationale = ' '.join(roles[channel] for channel in channels)
            h.guardrail = 'Track funded-account quality and cost; avoid interpreting clicks as acquired accounts.'
            h.client_question = 'Which annual goal and acquisition barrier should this concept address?'
        return Analysis(hypotheses=hypotheses, takeaway=StrategistTakeaway(finding='The recorded checking pages show fees and opening-funding requirements with qualifications.', implication='Test clearer terms and switching guidance, after validating the client goal and actual customer friction.', client_question='Is the priority more funded accounts, primary relationships, or resolving a specific acquisition problem?', source_ids=available[:2]))

    def benchmarks(self, request, sources):
        return BenchmarkResearch(benchmarks=[], limitations='Recorded demo contains no verified public checking CPA benchmark. Use a labeled strategist assumption for a scenario; live mode researches public benchmarks. Curated outputs do not adapt to your client brief.')

    def critique(self, context):
        return RecommendationReview(findings=['Recorded campaigns are provisional: confirm client-goal fit and the actual acquisition barrier.', 'Public CPA is unavailable in this replay; do not present an assumed CPA as a benchmark.', 'Define a funded-account outcome and exclude duplicate conversions across channels.'], revision_instructions='Make account definition and cross-channel deduplication explicit in each campaign guardrail.')

    def revise(self, context):
        hypotheses = [Hypothesis(**h) for h in context['hypotheses']]
        for h in hypotheses:
            h.guardrail = 'Define a funded checking account with the client; deduplicate conversions across channels and monitor acquisition cost and activation.'
        takeaway = context.get('strategist_takeaway')
        return Analysis(hypotheses=hypotheses, takeaway=StrategistTakeaway(**takeaway) if takeaway else None)
