# Cache-write accounting fix

User authorized fixing cache-write tracking and updating the existing public app. Small corrective change, existing checkout/branch retained.

Root cause: price_tokens rejected all positive cache_creation counts and discarded writes. Ordinary input and cached reads alone cannot price these responses.

Implementation: capture cache writes and raw provider lifetime breakdown, validate non-overlapping read/write partitions and lifetime sums, price each input category once. Default implicit 30m applies because this app sends no cache lifetime overrides. Provider mixed lifetime details take precedence. Output reasoning stays inside output tokens. Missing counts, unknown models/tiers or invalid details stay unpriced with a status reason. No old run is reconstructed from missing counts.

Validation: test missing writes, default/mixed lifetimes, invalid partitions, unknown tiers, aggregate non-duplication and real SDK HTTP parsing-failure usage retention. Run complete suite, one small live cache-write probe, independent review and hosted recorded smoke test. Commit/push and reboot app to reload imported modules; refresh credential-free ZIP.

Sources: https://developers.openai.com/api/docs/guides/prompt-caching and https://developers.openai.com/api/docs/pricing (2026-10-24 snapshot). Write rates are total rates, not additive surcharges: 1.25x standard input for 30m and 2.5x for 12h.
