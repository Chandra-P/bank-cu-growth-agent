import json
import re

from .models import FACT_FIELDS


def evidence_fields(profile):
    """Stable display order: supported claims first, remaining gaps below."""
    return sorted(FACT_FIELDS.items(), key=lambda item: profile['facts'][item[0]]['status'] != 'Source-supported')


def comparison_fields(profiles):
    """Keep columns aligned while showing the most-supported rows first."""
    return sorted(FACT_FIELDS.items(), key=lambda item: -sum(p['facts'][item[0]]['status'] == 'Source-supported' for p in profiles))


def markdown_text(text):
    """Keep financial dollar amounts literal in Markdown math renderers."""
    return str(text).replace("$", "\\$")


def cell(text):
    return markdown_text(text).replace("|", " / ").replace("\n", " ")


def render_brief(state):
    request = state["request"]
    mode = "RECORDED EVIDENCE DEMO — curated extraction and hypotheses; no live Tavily or model calls" if state["mode"] == "recorded" else "LIVE RESEARCH — Tavily search and model-assisted analysis"
    approval = "Approved for export" if state.get("approved") else "Draft — human review required"
    lines = [f"# Checking growth intelligence", f"**{request['home']['name']} · {request['market']}**", f"{mode}", f"Run: `{state['run_id']}` · Created: {state['created_at']}", f"Status: {approval}", "", "Source-supported means an official-domain excerpt supports the extracted claim. It is not independent verification. Search snippets may be incomplete or stale. Not verified never means zero or no offer. Hypotheses are inference for human review.", "", "## Checking comparison", ""]
    profiles = state.get("profiles",[])
    lines += ['', '## Client discussion context', markdown_text(request.get('client_brief') or 'Not provided; confirm goals with the client.')]
    takeaway = state.get('strategist_takeaway')
    if takeaway:
        lines += ['', '## Strategist takeaway', markdown_text(takeaway['finding']), '**Implication:** '+markdown_text(takeaway['implication']), '**Client validation question:** '+markdown_text(takeaway['client_question']), '**Evidence:** '+', '.join(takeaway['source_ids'])]
    lines.append("| Field | " + " | ".join(cell(p["institution"]["name"]) for p in profiles) + " |")
    lines.append("| --- | " + " | ".join("---" for _ in profiles) + " |")
    for key,label in comparison_fields(profiles):
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
        lines += [f"### {i}. {markdown_text(h['title'])}", markdown_text(h["rationale"]), f"**Evidence:** {', '.join(h['source_ids'])}", f"**Experiment:** {markdown_text(h['experiment'])}", f"**Measure:** {markdown_text(h['success_metric'])}", f"**Limit:** {markdown_text(h['caveat'])}", ""]
        for field in ('audience','need_connection','message','channel_rationale','guardrail','client_question'):
            lines.append(f"**{field.replace('_',' ').capitalize()}:** {markdown_text(h.get(field,''))}")
        lines.append('**Channels:** '+', '.join(h.get('channels',[])))
    lines += ['', '## Review and revision', f"Accepted revision cycles: {state.get('revision_count',0)}"]
    lines += ['- '+markdown_text(f) for f in state.get('review_findings',[])]
    lines += ['', '## Public benchmark research', markdown_text(state.get('benchmarks',{}).get('limitations','Not available'))]
    for benchmark in state.get('benchmarks',{}).get('benchmarks',[]):
        lines.append(markdown_text(json.dumps(benchmark, ensure_ascii=False)))
    lines += ["## Gaps and review notes", ""]
    for profile in profiles:
        if profile["gaps"]:
            lines.append(f"- {profile['institution']['name']}: {', '.join(profile['gaps'])}.")
    lines += ["- " + w for w in state.get("warnings",[])]
    if state.get("approval",{}).get("note"):
        lines += ["", "Reviewer note: " + state["approval"]["note"]]
    lines += ["", "## Source register", ""]
    used = {f["source_id"] for p in profiles for f in p["facts"].values() if f["status"] == "Source-supported"} | {b['source_id'] for b in state.get('benchmarks',{}).get('benchmarks',[])}
    for source in state.get("sources",[]):
        if source["id"] in used:
            lines.append(f"- **{source['id']}**: [{cell(source['title'])}]({source['url']}) · Retrieved {source['retrieved_at']} · {source['collection']}")
    lines += ["", "Full supporting excerpts, fact-level quotes, approval metadata and the operation trace are included in the JSON export. Review current full disclosures, membership eligibility and offer expiration before using any finding in a campaign."]
    return "\n\n".join(lines[:7]) + "\n" + "\n".join(lines[7:])


def export_bundle(state):
    approval = state.get("approval",{})
    if not state.get("approved") or state.get("status") != "approved" or approval.get("approved") is not True or approval.get("run_id") != state.get("run_id"):
        raise PermissionError("Approve this run before exporting.")
    allowed = ["request","run_id","mode","created_at","status","approval","competitors","profiles","sources","hypotheses","strategist_takeaway","benchmarks","review_findings","revision_instructions","revision_count","draft_hypotheses","draft_takeaway","usage","warnings","trace"]
    payload = {k:state.get(k) for k in allowed}
    return render_brief(state), json.dumps(payload, ensure_ascii=False, indent=2)
