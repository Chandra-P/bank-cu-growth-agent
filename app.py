"""Run with: python -m streamlit run app.py"""
from pathlib import Path
from uuid import uuid4

import streamlit as st
from langgraph.types import Command
from pydantic import ValidationError

from growth.demo import DemoSearch, DemoAnalyst, demo_request
from growth.evidence import confirm_competitors, reviewed_competitor
from growth.graph import build_graph, new_state
from growth.models import Institution, ResearchRequest, FACT_FIELDS
from growth.providers import TavilySearch, LiveAnalyst
from growth.report import export_bundle, markdown_text

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="FI growth intelligence", page_icon=":material/account_balance:", layout="wide", initial_sidebar_state="auto")
# Tables otherwise expose an independent CSV/clipboard path before review.
st.set_option("client.disableDataExport", True)

for key, value in {"graph":None, "config":None, "result":None, "run_error":None}.items():
    st.session_state.setdefault(key,value)


def reset_research():
    for key in ["graph", "config", "result", "run_error"]:
        st.session_state[key] = None
    for key in list(st.session_state):
        if key.startswith(("candidate_", "review_")) or key == "reviewed_evidence":
            del st.session_state[key]


def clear_credentials():
    # The graph closes over provider clients, so discard it with the keys.
    reset_research()
    st.session_state["visitor_openai_key"] = ""
    st.session_state["visitor_tavily_key"] = ""


def advance(payload):
    st.session_state.run_error = None
    try:
        with st.status("Working through the research workflow…", expanded=True) as status:
            labels = {"discover":"Discovering competitor candidates", "confirm":"Competitor set confirmed", "collect":"Collecting public-source evidence", "extract":"Checking extracted facts and research gaps", "save_profile":"Institution profile assembled", "analyze":"Drafting growth hypotheses", "review":"Review decision recorded"}
            for event in st.session_state.graph.stream(payload, st.session_state.config, stream_mode="updates"):
                for node in event:
                    if node in labels:
                        status.write(labels[node])
            st.session_state.result = dict(st.session_state.graph.get_state(st.session_state.config).values)
            status.update(label="Ready for your next decision", state="complete", expanded=False)
    except (ValueError, ValidationError, KeyError):
        st.session_state.run_error = "The input or saved response could not be validated. Check the institution names and official domains, then retry or start a new run."
    except Exception:
        st.session_state.run_error = "The run could not finish this step. Check your local configuration and provider access, then start a new run. Provider details and credentials are not displayed."


with st.sidebar:
    st.badge("FI / GROWTH",icon=":material/account_balance:",color="blue")
    st.markdown("## Know your market.\n## Choose your next move.")
    st.caption("Competitive insight for banks and credit unions.")
    st.divider()
    st.caption("RESEARCH WORKSPACE")
    active = st.session_state.result is not None
    mode = st.selectbox("Research mode", ["Recorded evidence demo", "Live research"], disabled=active, key="mode")
    recorded = mode == "Recorded evidence demo"
    if recorded:
        with st.expander("About the recorded demo",icon=":material/info:"):
            st.caption("Official-page excerpts collected October 24, 2026. Curated extraction and hypotheses; no live search or model calls.")
    st.caption("CONNECT YOUR KEYS")
    openai_key = st.text_input("OpenAI API key", type="password", key="visitor_openai_key", disabled=active, max_chars=300)
    tavily_key = st.text_input("Tavily API key", type="password", key="visitor_tavily_key", disabled=active, max_chars=300)
    st.caption("Keys are sent to this app's server and held in your session memory for provider calls. Provider charges apply. They are not written to reports or saved to disk.")
    st.button("Clear keys & session", key="clear_keys", on_click=clear_credentials, icon=":material/lock_reset:", width="stretch")
    with st.expander("Model settings", icon=":material/settings:"):
        model_name = st.text_input("OpenAI model", "gpt-6-luna", max_chars=100, disabled=active, key="visitor_model")
        st.caption("Use a model available to your OpenAI API project. Keys are never loaded from the host environment.")
    ready = bool(openai_key.strip() and tavily_key.strip() and model_name.strip())
    if not recorded and not ready:
        st.info("Enter both keys to start live research, or choose the recorded demo.")
    default = demo_request()
    with st.form("research_setup",border=False):
        name = st.text_input("Home institution", default.home.name, disabled=recorded or active, max_chars=120)
        domain = st.text_input("Official domain", default.home.domain, disabled=recorded or active)
        market = st.text_input("Market", default.market, disabled=recorded or active, max_chars=160)
        st.caption("Consumer checking · 3 competitors")
        with st.expander("Demo controls",icon=":material/tune:"):
            outage = st.checkbox("Simulate a Skyla source outage", disabled=not recorded or active, key="demo_outage", help="Demonstrates one retry, then an explicit unknown instead of an invented answer.")
        start = st.form_submit_button("Explore recorded demo" if recorded else "Start live research", type="primary", disabled=active or (not recorded and not ready), key="start_research", icon=":material/search:",width="stretch")
    if start:
        try:
            request = default if recorded else ResearchRequest(home=Institution(name=name,domain=domain),market=market)
            if recorded:
                search, analyst = DemoSearch(outage=outage), DemoAnalyst()
            else:
                if not ready:
                    raise ValueError("Visitor credentials required")
                search = TavilySearch(tavily_key.strip())
                analyst = LiveAnalyst(openai_key.strip(),model_name.strip(),"https://api.openai.com/v1")
            st.session_state.graph = build_graph(search,analyst)
            st.session_state.config = {"configurable":{"thread_id":str(uuid4())},"recursion_limit":60}
            advance(new_state(request,"recorded" if recorded else "live"))
            st.rerun()
        except (ValueError,ValidationError):
            st.error("Check the institution, market and official domain. For live research, enter both API keys and a model in the research panel.")
    if st.button("New research", disabled=not active, key="new_research", icon=":material/add:",width="stretch"):
        reset_research()
        st.rerun()
    st.divider()
    st.caption(":material/public: Public sources · Human-reviewed output")
    with st.expander("Session & privacy",icon=":material/shield:"):
        st.caption("Runs and provider clients are scoped to your Streamlit session, not shared with other visitors. Clear keys & session discards them. Disconnect cleanup depends on the host; closing a tab does not promise immediate erasure. Download approved results to keep a copy.")

st.caption("FI / GROWTH     ·     WORKSPACE / COMPETITOR ANALYSIS")
st.title("Your market, in focus.")
st.markdown("Consumer checking intelligence for banks and credit unions.")

result = st.session_state.result
if st.session_state.run_error:
    st.error(st.session_state.run_error)

if not result:
    st.space("small")
    with st.container(border=True,key="scope_card"):
        st.badge("YOUR DEMO MARKET" if recorded else "YOUR RESEARCH MARKET",icon=":material/location_on:",color="blue")
        st.subheader("Truliant Federal Credit Union · Charlotte" if recorded else f"{name} · {market}")
        st.write("One market. Three competitors. A checking-account brief your growth team can inspect and act on.")
        st.caption("Recorded evidence demo · No API keys needed · Human approval before export" if recorded else "Live public-source research · Bring your own API keys · Human approval before export")
    st.space("small")
    steps = st.columns(3,gap="medium")
    with steps[0].container(border=True):
        st.badge("01 / DISCOVER",icon=":material/travel_explore:",color="blue")
        st.subheader("Map your alternatives")
        st.write("Review three candidate institutions and confirm the market you want to compare.")
    with steps[1].container(border=True):
        st.badge("02 / COMPARE",icon=":material/fact_check:",color="blue")
        st.subheader("See the terms clearly")
        st.write("Compare checking products with source evidence and explicit gaps.")
    with steps[2].container(border=True):
        st.badge("03 / DECIDE",icon=":material/experiment:",color="blue")
        st.subheader("Choose what to test")
        st.write("Review growth hypotheses, experiments and metrics before sharing your brief.")
    st.caption(":material/arrow_back: Explore the recorded demo or enter your own keys for live research in the research panel.")
    st.stop()

with st.container(horizontal=True,gap="small"):
    st.badge(result['request']['home']['name'],icon=":material/account_balance:",color="blue")
    st.badge(result['request']['market'],icon=":material/location_on:",color="blue")
if result["mode"] == "recorded":
    st.info("RECORDED DEMO · Curated evidence from October 24, 2026. No live search or model calls; recheck current terms before use.",icon=":material/history:")
else:
    st.info("LIVE RESEARCH · Model-extracted claims are checked against collected official-domain excerpts. Review current full disclosures before acting.")

status = result["status"]
st.progress({"awaiting competitors":.2,"researching":.45,"awaiting review":.85,"approved":1.,"rejected":1.}.get(status,.1), text=status.capitalize())

if status == "awaiting competitors":
    st.subheader("Confirm your comparison set")
    st.write("These are candidate alternatives, not a market-share ranking. Confirm the institution identity, local relevance and official website.")
    if not result["candidates"]:
        st.warning("Discovery did not produce a usable set. Enter three competitors manually.")
    with st.form("competitor_confirmation"):
        chosen = []
        for i in range(3):
            candidate = result["candidates"][i] if i < len(result["candidates"]) else {"name":"","domain":"","reason":"Manual selection"}
            with st.container(border=True):
                st.caption(f"COMPETITOR {i+1}")
                cols = st.columns([2,2])
                cname = cols[0].text_input("Institution name", candidate["name"], key=f"candidate_name_{i}", disabled=recorded)
                cdomain = cols[1].text_input("Official website domain", candidate["domain"], key=f"candidate_domain_{i}", disabled=recorded)
                st.caption(candidate["reason"])
                # Validate on submit below; don't attribute the old candidate's
                # discovery rationale to a manually substituted institution.
                chosen.append({"name":cname,"domain":cdomain,"candidate":candidate})
        confirmed = st.form_submit_button("Confirm and research", key="confirm_competitors", type="primary", icon=":material/play_arrow:")
    if confirmed:
        try:
            chosen = [reviewed_competitor(c["candidate"],c["name"],c["domain"]) for c in chosen]
            confirm_competitors(Institution(**result["request"]["home"]),[Institution(**c) for c in chosen])
            advance(Command(resume={"competitors":chosen}))
            st.rerun()
        except (ValueError,ValidationError):
            st.error("Enter exactly three distinct competitor names and official public domains, excluding your home institution.")
    st.stop()

profiles = result.get("profiles",[])
facts = [f for p in profiles for f in p["facts"].values()]
supported = sum(f["status"] == "Source-supported" for f in facts)
with st.container(horizontal=True, gap="small", wrap=True):
    cols = [st.container(width=210) for _ in range(4)]
cols[0].metric("Institutions",str(len(profiles)),border=True)
cols[1].metric("Evidence",f"{supported} / {len(facts)}",border=True,help="Source-supported fields out of all compared fields.")
cols[2].metric("Hypotheses",str(len(result["hypotheses"])),border=True)
cols[3].metric("Review status",status.removeprefix("awaiting ").capitalize(),border=True)

brief, evidence, trace, method = st.tabs(["Comparison & opportunities","Evidence & gaps","Run trace","How it works"])
with brief:
    with st.container(border=True,key="comparison_card"):
        st.badge("MARKET SNAPSHOT",icon=":material/compare_arrows:",color="blue")
        st.subheader("How the checking offers compare")
        rows = [{"Field":label, **{p["institution"]["name"]:p["facts"][key]["value"] for p in profiles}} for key,label in FACT_FIELDS.items()]
        st.dataframe(rows,hide_index=True,height=365,alt="Checking product comparison for the home institution and three confirmed competitors")
        st.caption("Not verified = insufficient evidence. It does not mean zero fees, no requirement, or no available offer.")
    st.subheader("Three opportunities to test")
    st.caption("Inference for human review · no promised uplift or unverified claims of product superiority")
    opportunity_columns = st.columns(3, gap="medium")
    for i,h in enumerate(result["hypotheses"],1):
        with opportunity_columns[(i-1) % 3].container(border=True,key=f"opportunity_card_{i}"):
            st.badge(f"OPPORTUNITY {i:02d}",icon=":material/experiment:",color="blue")
            st.markdown(f"#### {i}. {markdown_text(h['title'])}")
            st.write(markdown_text(h["rationale"]))
            with st.expander("Experiment & success metric"):
                st.caption("THE EXPERIMENT")
                st.write(markdown_text(h["experiment"]))
                st.caption("WHAT TO MEASURE")
                st.write(markdown_text(h["success_metric"]))
            with st.expander("Evidence & limitations",icon=":material/policy:"):
                st.caption("Limit: " + markdown_text(h["caveat"]))
                st.caption("Evidence: " + ", ".join(h["source_ids"]))
    if result["warnings"]:
        with st.expander("Research limitations",expanded=True):
            for warning in result["warnings"]:
                st.warning(warning)

with evidence:
    st.subheader("Follow each finding to its source")
    st.caption("The checks enforce source identity, an exact excerpt match, and numeric consistency. They do not establish semantic correctness or completeness; human review remains necessary.")
    sources = {s["id"]:s for s in result["sources"]}
    for profile in profiles:
        with st.expander(profile["institution"]["name"],expanded=False):
            for key,label in FACT_FIELDS.items():
                fact = profile["facts"][key]
                st.markdown(f"**{label}:** {markdown_text(fact['value'])}")
                if fact["status"] == "Source-supported":
                    source = sources[fact["source_id"]]
                    st.text(f"Supporting excerpt: {fact['quote']}")
                    st.link_button("Open official source",source["url"],icon=":material/open_in_new:")
                    st.caption(f"{source['id']} · Retrieved {source['retrieved_at']} · {source['collection']}")
            st.caption("Gaps: " + ", ".join(profile["gaps"]))

with trace:
    st.subheader("Decisions and tool outcomes")
    st.caption("Operational events only. No private model reasoning or API credentials are stored here.")
    st.dataframe(result["trace"],hide_index=True,alt="Agent operation trace showing retries, evidence checks, and research routing")
    st.caption("Run ID: " + result["run_id"])

with method:
    st.subheader("A small, stateful agent system")
    st.code("Discover → HUMAN CONFIRMS → Search → Extract → Gap decision\n                                      ↑              │\n                                      └─ one follow-up┘\n              → Next institution → Analyze → HUMAN REVIEWS → Export",language=None)
    st.write("Discovery chooses candidates. Research chooses a follow-up search when evidence is incomplete. Analysis proposes evidence-linked growth tests. LangGraph holds state and pauses for your two decisions.")
    st.write("Limits: three competitors, two search rounds per institution, five results per search, one retry per remote operation. Memory is scoped to this session. Public product evidence only; no campaign publishing.")

st.divider()
if status == "awaiting review":
    with st.container(border=True,key="review_card"):
        st.badge("HUMAN CHECKPOINT",icon=":material/verified_user:",color="blue")
        st.subheader("Ready to share this brief?")
        st.write("Review the evidence, missing terms and proposed tests. Your approval enables downloads; it does not publish a campaign.")
        note = st.text_area("Reviewer notes",key="review_note",max_chars=1000,placeholder="Record caveats or follow-up checks for your team.")
        reviewed = st.checkbox("I reviewed the evidence and understand the gaps and hypotheses.",key="reviewed_evidence")
        with st.container(horizontal=True):
            approve = st.button("Approve and enable downloads",key="approve_report",type="primary",disabled=not reviewed,icon=":material/check:")
            reject = st.button("Reject this brief",key="reject_report",icon=":material/close:")
    if approve or reject:
        advance(Command(resume={"approve":bool(approve and reviewed),"note":note}))
        st.rerun()
elif status == "approved":
    st.success("Approved for export. The report retains its evidence, limitations and reviewer note.")
    md,js = export_bundle(result)
    with st.container(horizontal=True):
        st.download_button("Download briefing",md,file_name="checking-growth-brief.md",mime="text/markdown",key="download_brief",icon=":material/download:")
        st.download_button("Download evidence & trace",js,file_name="checking-growth-evidence.json",mime="application/json",key="download_evidence",icon=":material/data_object:")
elif status == "rejected":
    st.warning("Brief rejected. Downloads are unavailable. Start new research to change the scope or collect better evidence.")
