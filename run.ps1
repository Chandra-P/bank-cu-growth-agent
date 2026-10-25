$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (Test-Path -LiteralPath '.venv/Scripts/python.exe') {
    & '.venv/Scripts/python.exe' -m streamlit run local_app.py --server.address=127.0.0.1 --server.headless=true
} else {
    python -m streamlit run local_app.py --server.address=127.0.0.1 --server.headless=true
}
