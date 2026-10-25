# Blue dashboard design

The user-approved image reference supplies the visual direction: blue sidebar, blue overview banner, light gray canvas, white cards, subtle shadows, and colored metric accents. It does not supply business data or workflow instructions.

The overview identifies the FI, market and actual run status. It presents four workflow stages without simulated campaign performance. Native Streamlit controls remain responsible for research, confirmation, review and export. Setup collapses once a run exists and can be reopened to change mode or client. KPI cards use actual institution/evidence/campaign counts and the existing cost ledger, with partial totals labeled. Recorded replay remains explicitly labeled and has no paid calls.

The banner is isolated HTML with escaped dynamic values and no JavaScript. Card surfaces use explicit Streamlit container keys; no widget event behavior or hidden data is changed. Theme tokens control the sidebar, forms, tables and semantic colors. The banner responds to narrow layouts with a two-column stage grid. Secrets, provider clients, evidence checks and approval gates are unchanged.
