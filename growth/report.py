import json
import re

from .models import FACT_FIELDS


def cell(text):
    return str(text).replace("|", " / ").replace("\n", " ")


def render_brief(state):
    request = state["request"]
    mode = "RECORDED EVIDENCE DEMO — curated extraction and hypotheses; no live Tavily or model calls" if state["mode"] == "recorded" else "LIVE RESEARCH — Tavily search and model-assisted analysis"
    approval = "Approved for export" if state.get("approved") else "Draft — human review required"
    lines = [f"# Checking growth intelligence", f"**{request['home']['name']} · {request['market']}**", f"{mode}", f"Run: `{state['run_id']}` · Created: {state['created_at']}", f"Status: {approval}", "", "Source-supported means an official-domain excerpt supports the extracted claim. It is not independent verification. Search snippets may be incomplete or stale. Not verified never means zero or no offer. Hypotheses are inference for human review.", "", "## Checking comparison", ""]
    profiles = state.get("profiles",[])
    lines.append("| Field | " + " | ".join(cell(p["institution"]["name"]) for p in profiles) + " |")
    lines.append("| --- | " + " | ".join("---" for _ in profiles) + " |")
    for key,label in FACT_FIELDS.items():
        values = []
        for profile in profiles:
            fact = profile["facts"][key]
            value = cell(fact["value"])
            if fact["status"] == "Source-supported":
                value += f" [{fact['source_id']}]"
            values.append(value)
        lines.append("| " + label + " | " + " | ".join(values) + " |")
    lines += ["", "## Growth hypotheses — inference, not measured outcomes", ""]
    for i,h in enumerate(state.get("hypotheses",[]),1):
        lines += [f"### {i}. {h['title']}", h["rationale"], f"**Evidence:** {', '.join(h['source_ids'])}", f"**Experiment:** {h['experiment']}", f"**Measure:** {h['success_metric']}", f"**Limit:** {h['caveat']}", ""]
    lines += ["## Gaps and review notes", ""]
    for profile in profiles:
        if profile["gaps"]:
            lines.append(f"- {profile['institution']['name']}: {', '.join(profile['gaps'])}.")
    lines += ["- " + w for w in state.get("warnings",[])]
    if state.get("approval",{}).get("note"):
        lines += ["", "Reviewer note: " + state["approval"]["note"]]
    lines += ["", "## Source register", ""]
    used = {f["source_id"] for p in profiles for f in p["facts"].values() if f["status"] == "Source-supported"}
    for source in state.get("sources",[]):
        if source["id"] in used:
            lines.append(f"- **{source['id']}**: [{cell(source['title'])}]({source['url']}) · Retrieved {source['retrieved_at']} · {source['collection']}")
    lines += ["", "Full supporting excerpts, fact-level quotes, approval metadata and the operation trace are included in the JSON export. Review current full disclosures, membership eligibility and offer expiration before using any finding in a campaign."]
    return "\n\n".join(lines[:7]) + "\n" + "\n".join(lines[7:])


def export_bundle(state):
    approval = state.get("approval",{})
    if not state.get("approved") or state.get("status") != "approved" or approval.get("approved") is not True or approval.get("run_id") != state.get("run_id"):
        raise PermissionError("Approve this run before exporting.")
    allowed = ["request","run_id","mode","created_at","status","approval","competitors","profiles","sources","hypotheses","warnings","trace"]
    payload = {k:state.get(k) for k in allowed}
    return render_brief(state), json.dumps(payload, ensure_ascii=False, indent=2)
