# Public deployment — bring your own keys

Use a Python-capable host. The existing Streamlit/LangGraph service needs a running Python process and WebSocket support; a static website upload cannot run it.

## Streamlit Community Cloud

1. Publish this project directory as the repository root on GitHub. Exclude `.env`, `.streamlit/secrets.toml`, runtime data, virtual environments and caches. Do not upload the containing workspace or other projects.
2. Sign in at https://share.streamlit.io and select the repository and branch.
3. Set the entry point to `app.py` and Python to **3.12** in advanced settings. `requirements.txt` pins the tested packages.
4. Leave app secrets empty. Each visitor supplies OpenAI and Tavily keys through the app. Select public access in the host's sharing controls.
5. Open the HTTPS app URL in a new browser session: recorded demo must work without keys; live mode must require both keys. Verify clearing keys resets the active run and two browser sessions do not share inputs or reports.

Official reference: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Container alternative

Build `docker build -t fi-growth .` and run `docker run --rm -p 8501:8501 fi-growth`. The Docker build context excludes credentials via `.dockerignore`. Use a host with HTTPS termination and WebSocket support. No model or search keys should be configured as host secrets.

## Data handling

Keys are masked on screen, transmitted to the app server over the hosting connection, and retained in the visitor's session memory for remote API calls. They are not browser-only credentials. The clear action discards the graph as well as the inputs because graph closures hold provider clients. There is no shared credential cache or durable run store. Host operators control the runtime; visitors should trust the host before providing credentials. Disable external request-body capture and tracing when operating the service.

Keep provider usage limits and workflow bounds in place. The app searches public product pages; it accepts no customer records. Reports retain evidence gaps and require explicit human approval before download.

## Current release status

Prepared locally. Public publication still requires authenticated GitHub and hosting access; no public URL has been created by this revision.
