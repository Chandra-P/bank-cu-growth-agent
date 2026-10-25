# Local saved keys, public BYOK

User explicitly requested automatic local .env credentials, public visitor keys only, and opening localhost for United Heritage Credit Union.

Use separate local_app.py entry guarded by a loopback server.address before reading any .env. It injects settings into app.py via runpy globals. Public app.py never reads the file or process environment keys. run.ps1 launches local_app.py bound to 127.0.0.1. Docker/public deployment remains app.py. Saved keys stay server-side, not in password widgets; visitor overrides remain possible locally. Clear keys & session disables saved-key fallback until explicitly re-enabled. Local entry defaults Live research. No changes to official OpenAI endpoint or billing ownership.

Tests: local key availability without prefilled secrets, clear disables fallback, non-loopback refuses before reading, public entry does not call local loader; all prior credentials/reset/export regressions. Fresh security review, browser localhost verification, then leave local server running and public deployment untouched. No .env contents go to Git or exports.
