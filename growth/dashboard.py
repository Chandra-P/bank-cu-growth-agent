"""Presentation only; no provider calls or workflow state changes."""
from html import escape
import streamlit as st


def overview_banner(name, market, status):
    # All dynamic content is escaped; this component has no JavaScript or actions.
    st.html(f"""<section class="fi-overview" aria-label="Research overview">
      <div class="fi-eyebrow">FI GROWTH INTELLIGENCE</div>
      <div class="fi-overview-heading"><h2>Your next growth conversation starts here.</h2>
        <span class="fi-status">{escape(status)}</span></div>
      <p>{escape(name or 'Choose a bank or credit union')} <span aria-hidden="true"> · </span> {escape(market or 'Select your market')}</p>
      <div class="fi-stages">
        <div><span>01</span><strong>Discover</strong><small>Confirm your competitive set</small></div>
        <div><span>02</span><strong>Research</strong><small>Inspect checking evidence</small></div>
        <div><span>03</span><strong>Recommend</strong><small>Shape campaign concepts</small></div>
        <div><span>04</span><strong>Review</strong><small>Approve before sharing</small></div>
      </div>
    </section>
    <style>
    .fi-overview {{background:linear-gradient(115deg,#126CB0,#0B4D7E);color:white;padding:28px;border-radius:18px;box-shadow:0 12px 24px #17466b18;position:relative;overflow:hidden;margin:4px 0 14px}}
    .fi-overview:after {{content:'';position:absolute;width:260px;height:260px;border-radius:50%;background:#ffffff07;right:-80px;top:-110px;pointer-events:none}}
    .fi-eyebrow {{font-size:11px;font-weight:650;letter-spacing:1.6px;color:#D1E9FC;margin-bottom:10px}}
    .fi-overview-heading {{display:flex;align-items:center;justify-content:space-between;gap:18px}}
    .fi-overview h2 {{font:650 27px/1.25 Inter,sans-serif;color:white;margin:0;letter-spacing:-.5px}}
    .fi-overview p {{color:#D4E9F8;font-size:14px;margin:12px 0 22px}}
    .fi-status {{background:#ffffff20;border:1px solid #ffffff30;border-radius:20px;padding:6px 12px;font-size:12px;white-space:nowrap}}
    .fi-stages {{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
    .fi-stages>div {{background:#ffffff10;border:1px solid #ffffff22;border-radius:12px;padding:14px}}
    .fi-stages span {{display:inline-flex;background:#ffffff20;border-radius:7px;padding:4px 7px;font-size:11px;margin-bottom:9px}}
    .fi-stages strong {{display:block;font-size:14px;font-weight:600}}
    .fi-stages small {{display:block;color:#D4E9F8;font-size:11px;margin-top:5px}}
    @media(max-width:700px) {{.fi-overview{{padding:20px}} .fi-overview h2{{font-size:23px}} .fi-overview-heading{{align-items:flex-start;flex-direction:column;gap:10px}} .fi-stages{{grid-template-columns:repeat(2,1fr)}}}}
    </style>
    """)


def card_surfaces():
    # Streamlit's explicit container keys give these surfaces stable scopes.
    st.html("""<style>
    .st-key-client_setup,.st-key-scope_card,.st-key-comparison_card,
    .st-key-takeaway_card,.st-key-review_card,.st-key-kpi_institutions,
    .st-key-kpi_evidence,.st-key-kpi_hypotheses,.st-key-kpi_cost,
    .st-key-opportunity_card_1,.st-key-opportunity_card_2,.st-key-opportunity_card_3 {
      background:#fff;border-radius:14px;box-shadow:0 2px 4px #1b35500a;
    }
    </style>""")
