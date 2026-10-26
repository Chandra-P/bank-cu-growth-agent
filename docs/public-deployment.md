# Deployment

## Public Streamlit Cloud app

Repository: https://github.com/Chandra-P/bank-cu-growth-agent

Branch: `submission`. Entry point: `app.py`. Python: 3.12.

Public URL: https://bank-cu-growth-intelligence.streamlit.app/

Deploy the project directory as repository root. Do not upload `.env`, secret files, virtual environments or runtime data. Leave hosted API secrets empty: live visitors supply their own OpenAI and Tavily keys. Recorded mode works without keys.

After imported module or graph schema changes, reboot the app cleanly and verify a fresh session. Check that recorded mode starts, live mode requires visitor keys, changing client clears prior results, and approval gates downloads.

## Local development

Use `run.ps1` or `python -m streamlit run local_app.py --server.address=127.0.0.1 --server.headless=true`. The separate local entry point checks loopback before reading saved `.env` keys. Do not use it as the public entry point.

## Container

```powershell
docker build -t fi-growth .
docker run --rm -p 8501:8501 fi-growth
```

Provide HTTPS and WebSocket support on the host. Docker uses `app.py`; the build context excludes credential files.

## Data handling

Visitor keys reach the application server and remain in session memory for provider calls. No shared credential cache or durable customer database is used. Clear keys and session discards the active run and provider references. Avoid request-body logging and protect host access.
