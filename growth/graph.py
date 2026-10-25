from __future__ import annotations

from datetime import datetime, timezone
from typing import TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt

from .evidence import confirm_competitors, ground_fact
from .models import Institution, Source, Profile, Fact, FACT_FIELDS, ResearchRequest
from .providers import bounded_call, ProviderError


class RunState(TypedDict, total=False):
    request: dict
    run_id: str
    mode: str
    created_at: str
    status: str
    approved: bool
    approval: dict
    candidates: list[dict]
    competitors: list[dict]
    profiles: list[dict]
    sources: list[dict]
    active_sources: list[dict]
    current_profile: dict
    index: int
    round: int
    hypotheses: list[dict]
    warnings: list[str]
    trace: list[dict]


def new_state(request: ResearchRequest, mode: str) -> RunState:
    return dict(request=request.model_dump(), run_id=str(uuid4()), mode=mode, created_at=datetime.now(timezone.utc).isoformat(), status="discovering", approved=False, approval={}, candidates=[], competitors=[], profiles=[], sources=[], active_sources=[], current_profile={}, index=0, round=0, hypotheses=[], warnings=[], trace=[])


def build_graph(search, analyst):
    def discover(state):
        request = ResearchRequest(**state["request"])
        if state["mode"] != search.mode or state["mode"] != analyst.mode:
            raise ValueError("Provider mode does not match the run.")
        if state["mode"] == "recorded":
            from .demo import demo_request
            expected = demo_request()
            if request.home.domain != expected.home.domain or request.market != expected.market:
                raise ValueError("Recorded demo supports only Truliant in Charlotte. Use live mode for another scope.")
        trace, warnings = list(state["trace"]), list(state["warnings"])
        candidates = []
        try:
            sources = bounded_call(lambda:search.search(f"{request.market} banks credit unions consumer checking accounts competitors {request.home.name}"), "discovery:search", trace)
            candidates = bounded_call(lambda:analyst.discover(state["request"], sources), "discovery:agent", trace)
            candidates = confirm_competitors(request.home, candidates)
        except (ProviderError, ValueError):
            warnings.append("Competitor discovery was incomplete. Enter three official institution names and domains to continue.")
            sources = []
        return {"candidates":[c.model_dump() for c in candidates], "trace":trace, "warnings":warnings, "status":"awaiting competitors", "sources": [s.model_dump() for s in sources]}

    def confirm(state):
        answer = interrupt({"stage":"competitors", "candidates":state["candidates"], "message":"Confirm three competitors and their official domains before research."})
        competitors = confirm_competitors(Institution(**state["request"]["home"]), [Institution(**c) for c in answer["competitors"]])
        if state["mode"] == "recorded":
            from .demo import fixture
            if [c.domain for c in competitors] != [c["domain"] for c in fixture()["competitors"]]:
                raise ValueError("Use live mode to change the recorded competitor set.")
        return {"competitors":[c.model_dump() for c in competitors], "status":"researching"}

    def collect(state):
        institutions = [state["request"]["home"], *state["competitors"]]
        institution = Institution(**institutions[state["index"]])
        query = f"{institution.name} consumer checking account monthly maintenance fee minimum opening deposit balance fee waivers membership eligibility bonus terms positioning recent news {state['request']['market']}"
        if state["round"]:
            query = f"{institution.name} {state['current_profile'].get('follow_up','checking terms')}"
        trace, warnings = list(state["trace"]), list(state["warnings"])
        try:
            sources = bounded_call(lambda:search.search(query, institution.domain), f"search:{institution.domain}:{state['round']+1}", trace)
        except ProviderError:
            sources = []
            warnings.append(f"{institution.name}: search unavailable in round {state['round']+1}; unsupported fields remain Not verified.")
        active = {s["id"]:s for s in state["active_sources"]}
        active.update({s.id:s.model_dump() for s in sources})
        all_sources = {s["id"]:s for s in state["sources"]}
        all_sources.update(active)
        return {"active_sources":list(active.values()), "sources":list(all_sources.values()), "trace":trace, "warnings":warnings}

    def extract(state):
        institution = Institution(**([state["request"]["home"], *state["competitors"]][state["index"]]))
        sources = [Source(**s) for s in state["active_sources"]]
        trace, warnings = list(state["trace"]), list(state["warnings"])
        facts, follow_up = {}, ""
        if sources:
            try:
                extraction = bounded_call(lambda:analyst.extract(institution, sources), f"extract:{institution.domain}", trace)
                facts = extraction.facts
                follow_up = extraction.follow_up
            except ProviderError:
                warnings.append(f"{institution.name}: extraction unavailable; review source pages manually.")
        grounded = {key:ground_fact(facts.get(key, Fact()), sources, institution) for key in FACT_FIELDS}
        if grounded["product_name"].status != "Source-supported":
            grounded = {key:Fact() for key in FACT_FIELDS}
            follow_up = "identify one current consumer checking product by name and its official fee schedule, opening deposit and conditions" if sources else ""
            if state["round"] == 1 or not sources:
                warnings.append(f"{institution.name}: product identity could not be confirmed; comparison terms are withheld to avoid mixing products.")
        gaps = [FACT_FIELDS[k] for k,f in grounded.items() if f.status == "Not verified"]
        profile = Profile(institution=institution, facts=grounded, follow_up=follow_up if gaps else "", gaps=gaps)
        trace.append({"action":f"evidence:{institution.domain}", "outcome":"checked", "supported":len(FACT_FIELDS)-len(gaps), "unknown":len(gaps), "next":"follow-up" if profile.follow_up and state["round"] == 0 else "next institution"})
        return {"current_profile":profile.model_dump(), "round":state["round"]+1, "trace":trace, "warnings":warnings}

    def save_profile(state):
        return {"profiles":[*state["profiles"], state["current_profile"]], "index":state["index"]+1, "round":0, "active_sources":[], "current_profile":{}}

    def analyze(state):
        trace, warnings = list(state["trace"]), list(state["warnings"])
        supported_ids = {f["source_id"] for p in state["profiles"] for f in p["facts"].values() if f["status"] == "Source-supported"}
        hypotheses = []
        if supported_ids:
            try:
                proposed = bounded_call(lambda:analyst.analyze(state["request"], state["profiles"]), "analysis:agent", trace)
                hypotheses = [h.model_dump() for h in proposed if h.source_ids and set(h.source_ids).issubset(supported_ids)][:3]
            except ProviderError:
                warnings.append("Analysis unavailable. Source-backed comparison is available for manual review; no substitute model output was invented.")
        if len(hypotheses) != 3:
            warnings.append("Fewer than three evidence-linked hypotheses are available. This is a partial result; retry or complete manual analysis before submission.")
        return {"hypotheses":hypotheses, "trace":trace, "warnings":warnings, "status":"awaiting review"}

    def review(state):
        answer = interrupt({"stage":"review", "run_id":state["run_id"], "message":"Review evidence, missing terms and hypotheses. Approve to enable export, or reject to end this run."})
        approved = answer.get("approve") is True
        return {"approved":approved, "approval":{"approved":approved, "run_id":state["run_id"], "note":str(answer.get("note", ""))[:1000], "at":datetime.now(timezone.utc).isoformat()}, "status":"approved" if approved else "rejected"}

    builder = StateGraph(RunState)
    for name, fn in [("discover",discover), ("confirm",confirm), ("collect",collect), ("extract",extract), ("save_profile",save_profile), ("analyze",analyze), ("review",review)]:
        builder.add_node(name, fn)
    builder.add_edge(START,"discover")
    builder.add_edge("discover","confirm")
    builder.add_edge("confirm","collect")
    builder.add_edge("collect","extract")
    builder.add_conditional_edges("extract",lambda s:"collect" if s["round"] < 2 and s["current_profile"].get("follow_up") else "save_profile",["collect","save_profile"])
    builder.add_conditional_edges("save_profile",lambda s:"collect" if s["index"] < 4 else "analyze",["collect","analyze"])
    builder.add_edge("analyze","review")
    builder.add_edge("review",END)
    return builder.compile(checkpointer=InMemorySaver())
