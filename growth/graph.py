from __future__ import annotations

from datetime import datetime, timezone
from typing import TypedDict
from uuid import uuid4
import re
from decimal import Decimal

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt

from .evidence import confirm_competitors, ground_fact, normalized
from .models import Institution, Source, Profile, Fact, FACT_FIELDS, ResearchRequest, Analysis
from .providers import bounded_call, ProviderError
from .discovery import discovery_questions
from .models import ClientDiscovery


class RunState(TypedDict, total=False):
    decision: str
    discovery_questions: list[str]
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
    strategist_takeaway: dict | None
    warnings: list[str]
    trace: list[dict]
    usage: list[dict]
    benchmarks: dict
    review_findings: list[str]
    revision_instructions: str
    revision_count: int
    draft_hypotheses: list[dict]
    draft_takeaway: dict | None


def new_state(request: ResearchRequest, mode: str) -> RunState:
    return dict(request=request.model_dump(), run_id=str(uuid4()), mode=mode, created_at=datetime.now(timezone.utc).isoformat(), status="discovering", approved=False, approval={}, candidates=[], competitors=[], profiles=[], sources=[], active_sources=[], current_profile={}, index=0, round=0, hypotheses=[], strategist_takeaway=None, warnings=[], trace=[], usage=[], benchmarks={}, review_findings=[], revision_instructions='', revision_count=0, draft_hypotheses=[], draft_takeaway=None)


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
                if state['round'] and state.get('current_profile'):
                    previous = Profile(**state['current_profile'])
                    if previous.institution.domain == institution.domain:
                        warnings.append(f"{institution.name}: previous grounded findings retained after the follow-up extraction outage; gaps remain unresolved.")
                        trace.append({'action':f'evidence:{institution.domain}', 'outcome':'previous grounded profile retained', 'next':'next institution'})
                        return {'current_profile':previous.model_dump(), 'round':state['round']+1, 'trace':trace, 'warnings':warnings}
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
        return {"profiles":[*state["profiles"], state["current_profile"]], "index":state["index"]+1, "round":0, "active_sources":[], "current_profile":{}, 'status':'awaiting discovery' if state['index']==3 else 'researching'}

    def discovery_checkpoint(state):
        # The recorded replay keeps its curated legacy scenario. Explicitly
        # supplied discovery (including {}) always exercises the real gate.
        if state['mode']=='recorded' and state['request'].get('client_discovery') is None:
            return {'decision':'recorded scenario', 'discovery_questions':[]}
        answer = interrupt({'stage':'discovery', 'message':'Confirm the client goal, observed problem and success definition before campaign planning.'})
        brief = ClientDiscovery(**answer)
        request = {**state['request'], 'client_discovery':brief.model_dump()}
        questions = discovery_questions(brief.model_dump())
        trace = [*state['trace'], {'agent':'Strategy', 'action':'strategy:discovery-checkpoint', 'outcome':'discovery needed' if questions else 'campaign planning ready'}]
        return {'request':request, 'decision':'discovery needed' if questions else 'campaign planning ready', 'discovery_questions':questions, 'trace':trace,
                'hypotheses':[], 'strategist_takeaway':None, 'review_findings':[], 'revision_instructions':'', 'revision_count':0, 'draft_hypotheses':[], 'draft_takeaway':None,
                'approved':False, 'approval':{}, 'benchmarks':{}, 'status':'analyzing'}

    def analyze(state):
        trace, warnings = list(state["trace"]), list(state["warnings"])
        if state.get('decision') == 'discovery needed':
            trace.append({'agent':'Strategy', 'action':'strategy:readiness', 'outcome':'Campaign generation withheld; discovery questions prepared locally; no model call'})
            return {'hypotheses':[], 'strategist_takeaway':None, 'trace':trace, 'warnings':warnings, 'status':'awaiting review', 'benchmarks':{'benchmarks':[], 'limitations':'Benchmark research deferred until client discovery is complete; no CPA or budget inferred.'}}
        supported_ids = {f["source_id"] for p in state["profiles"] for f in p["facts"].values() if f["status"] == "Source-supported"}
        hypotheses, takeaway = [], None
        if supported_ids:
            try:
                proposed = bounded_call(lambda:analyst.analyze(state["request"], state["profiles"]), "analysis:agent", trace)
                candidates = proposed.hypotheses if isinstance(proposed, Analysis) else proposed
                hypotheses = [h.model_dump() for h in candidates if h.source_ids and set(h.source_ids).issubset(supported_ids)][:3]
                if isinstance(proposed, Analysis) and proposed.takeaway:
                    if set(proposed.takeaway.source_ids).issubset(supported_ids):
                        takeaway = proposed.takeaway.model_dump()
                    else:
                        warnings.append("Strategist takeaway withheld because its evidence references were unsupported.")
            except ProviderError:
                warnings.append("Analysis unavailable. Source-backed comparison is available for manual review; no substitute model output was invented.")
        if len(hypotheses) != 3:
            warnings.append("Fewer than three evidence-linked hypotheses are available. This is a partial result; retry or complete manual analysis before submission.")
        return {"hypotheses":hypotheses, "strategist_takeaway":takeaway, "trace":trace, "warnings":warnings, "status":"awaiting review"}

    def review(state):
        answer = interrupt({"stage":"review", "run_id":state["run_id"], "message":"Review evidence, missing terms and hypotheses. Approve to enable export, or reject to end this run."})
        approved = answer.get("approve") is True
        return {"approved":approved, "approval":{"approved":approved, "run_id":state["run_id"], "note":str(answer.get("note", ""))[:1000], "at":datetime.now(timezone.utc).isoformat()}, "status":"approved" if approved else "rejected"}

    def benchmarks(state):
        trace, warnings = list(state['trace']), list(state['warnings'])
        result = {'benchmarks':[], 'limitations':'Benchmark research unavailable. Enter a clearly labeled strategist CPA assumption.'}
        sources = []
        try:
            sources = bounded_call(lambda:search.search('bank credit union consumer checking account acquisition cost per funded account direct mail display paid social campaign benchmark case study'), 'benchmarks:search', trace)
            proposed = bounded_call(lambda:analyst.benchmarks(state['request'], sources), 'benchmarks:agent', trace)
            accepted = []
            for benchmark in proposed.benchmarks:
                source = next((s for s in sources if s.id == benchmark.source_id), None)
                if not source or normalized(benchmark.quote) not in normalized(source.excerpt):
                    warnings.append('A benchmark was withheld because its source quote could not be validated.')
                    continue
                amounts = {Decimal(n.replace(',', '')) for n in re.findall(r'\d[\d,]*(?:\.\d+)?', benchmark.quote)}
                if benchmark.cpa is not None and Decimal(str(benchmark.cpa)) not in amounts:
                    warnings.append('A benchmark CPA was withheld because its amount was absent from the quote.')
                    continue
                if benchmark.cpa is not None:
                    quote = normalized(benchmark.quote)
                    definition = normalized(benchmark.account_definition)
                    # Conservative unit gate: a matching number alone is not an account CPA.
                    account_unit = re.search(r'(?:cost|spend|cpa).{0,60}(?:per|/|each).{0,35}(?:checking|account)|(?:per|/|each).{0,35}(?:checking\s+)?account', quote)
                    wrong_unit = re.search(r'cost per (?:lead|click)|\bcpl\b|\bcpc\b', quote)
                    unsupported_definition = any(term in definition and term not in quote for term in ('funded','activated','opened','direct deposit'))
                    if 'checking' not in quote or not account_unit or wrong_unit or unsupported_definition:
                        warnings.append('A benchmark was withheld because its quote did not establish the checking-account CPA unit and stated conversion definition.')
                        continue
                accepted.append(benchmark.model_dump())
            result = {'benchmarks':accepted, 'limitations':proposed.limitations}
        except ProviderError:
            warnings.append('Benchmark research unavailable; no substitute CPA was invented.')
        all_sources = {s['id']:s for s in state['sources']}
        all_sources.update({s.id:s.model_dump() for s in sources})
        return {'benchmarks':result, 'sources':list(all_sources.values()), 'trace':trace, 'warnings':warnings}

    def strategy_context(state):
        return {k:state.get(k) for k in ('request','profiles','hypotheses','strategist_takeaway','benchmarks','review_findings','revision_instructions')}

    def critique(state):
        trace, warnings = list(state['trace']), list(state['warnings'])
        findings, instructions = [], ''
        if state['hypotheses']:
            try:
                result = bounded_call(lambda:analyst.critique(strategy_context(state)), 'strategy:review', trace)
                findings, instructions = result.findings, result.revision_instructions
            except ProviderError:
                warnings.append('Automated review unavailable. Original draft retained for human review.')
        return {'draft_hypotheses':state['hypotheses'], 'draft_takeaway':state.get('strategist_takeaway'), 'review_findings':findings, 'revision_instructions':instructions, 'trace':trace, 'warnings':warnings}

    def revise(state):
        trace, warnings = list(state['trace']), list(state['warnings'])
        result = {}
        if state.get('revision_instructions'):
            try:
                revised = bounded_call(lambda:analyst.revise(strategy_context(state)), 'strategy:revision', trace)
                supported = {f['source_id'] for p in state['profiles'] for f in p['facts'].values() if f['status']=='Source-supported'}
                cited = [h.source_ids for h in revised.hypotheses]
                if revised.takeaway:
                    cited.append(revised.takeaway.source_ids)
                if not all(ids and set(ids).issubset(supported) for ids in cited):
                    raise ValueError('Unsupported revision references')
                result = {'hypotheses':[h.model_dump() for h in revised.hypotheses], 'strategist_takeaway':revised.takeaway.model_dump() if revised.takeaway else None, 'revision_count':1}
            except (ProviderError, ValueError):
                warnings.append('Revision unavailable or unsupported. Original draft retained; review findings remain unresolved for the strategist.')
        return {**result, 'trace':trace, 'warnings':warnings, 'status':'awaiting review'}

    def tracked(fn):
        def call(state):
            result = fn(state)
            result['usage'] = [dict(e) for provider in (search, analyst) for e in getattr(provider, 'events', [])]
            result['usage'].sort(key=lambda e:e.get('started_at',''))
            return result
        return call

    builder = StateGraph(RunState)
    for name, fn in [("discover",discover), ("confirm",confirm), ("collect",collect), ("extract",extract), ("save_profile",save_profile), ('discovery_checkpoint',discovery_checkpoint), ("analyze",analyze), ('benchmarks',benchmarks), ('critique',critique), ('revise',revise), ("review",review)]:
        builder.add_node(name, tracked(fn))
    builder.add_edge(START,"discover")
    builder.add_edge("discover","confirm")
    builder.add_edge("confirm","collect")
    builder.add_edge("collect","extract")
    builder.add_conditional_edges("extract",lambda s:"collect" if s["round"] < 2 and s["current_profile"].get("follow_up") else "save_profile",["collect","save_profile"])
    builder.add_conditional_edges("save_profile",lambda s:"collect" if s["index"] < 4 else "discovery_checkpoint",["collect","discovery_checkpoint"])
    builder.add_edge('discovery_checkpoint','analyze')
    builder.add_conditional_edges('analyze',lambda s:'review' if s.get('decision')=='discovery needed' else 'benchmarks',['review','benchmarks'])
    builder.add_edge('benchmarks','critique')
    builder.add_edge('critique','revise')
    builder.add_edge('revise','review')
    builder.add_edge("review",END)
    return builder.compile(checkpointer=InMemorySaver())
