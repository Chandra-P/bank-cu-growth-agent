# Public fintech workspace implementation plan

**Goal:** Implement the selected Option 3 Figma concept in the existing Streamlit app and prepare public hosting with visitor-supplied credentials.

**Architecture:** Keep Python, LangGraph and Streamlit. Provider objects and graphs belong only to the visitor session. No process environment or shared credential cache supplies live keys. Clearing keys also discards graph objects holding credentials and resets the run.

**Spec:** User-selected Figma frame https://www.figma.com/design/qqSxUYc4w1CRQnbVBo6FuF?node-id=1-4, plus public deployment with bring-your-own keys.

**Constraints:** Retain evidence validation, recorded demo, confirmation and final human approval. Never bundle .env. OpenAI endpoint is fixed; visitors cannot route credentials to a custom host. Native responsive Streamlit controls adapt the desktop concept to smaller screens.

- [x] Add regression tests: server credentials do not populate visitor inputs; live research is blocked without both keys; two sessions remain independent; clearing removes keys and active graph.
- [x] Replace .env loading with password inputs, per-session provider construction and a clear-session callback.
- [x] Apply Figma colors, Inter typography, navy sidebar, cobalt actions, summary and opportunity cards using native theme/layout.
- [x] Run full tests, inspect the browser, update deployment docs, package without secrets. The available in-app preview is narrow; wrapping metrics were corrected there. Desktop composition follows the selected Figma design, but no separate desktop-width browser screenshot was available.
- [x] Identify publication blocker: Streamlit Cloud sign-in and refreshed GitHub authentication are required. Publication remains pending those account steps.

Review focus: credentials must not enter reports, logs, URL state or caches; clearing must remove provider references; recorded demo must remain key-free; live controls must not silently use environment keys; downloads must remain gated.

Ruling: preserve the Python stack and prepare Streamlit Community Cloud / Docker deployment. Sites uses a different runtime and would require rebuilding the backend; this revision avoids that scope expansion. GitHub credentials are expired and the hosting browser shows the sign-in page, so publication requires user account access.
