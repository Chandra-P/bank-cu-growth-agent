# Cache-write cost accounting

For known standard-text model rates, estimated AI cost includes ordinary input, cache reads, cache writes and output. Write tokens are a subset of input, not an additional token total. Reasoning is a subset of output.

Input cost = (ordinary input × input rate + cache reads × read rate + 30m writes × 30m write rate + 12h writes × 12h write rate) / 1,000,000.

The app sends no lifetime overrides: aggregate writes use OpenAI's implicit 30m default. A provider-reported lifetime breakdown takes precedence. The 30m write rate is 1.25× ordinary input; 12h is 2.5×. These are total write rates, not surcharges. GPT-6 Luna standard rates are $0.10 ordinary input, $0.01 reads, $0.125 30m writes, $0.25 12h writes and $0.50 output per million tokens (2026-10-24 snapshot).

Missing counts, invalid partitions/lifetime sums, unknown models and unsupported tiers remain unpriced. Known cost subtotals are explicitly partial. Rates and lifetime basis are stored on each event, including failed model-response validation attempts. Table and JSON export contain write counts and component costs. The UI shows write costs within input; it never adds them twice. Tavily credits remain separate.

Previous run events omitted write counts and cannot be reliably reconstructed. Start a new live analysis to obtain complete estimates. Costs remain estimates, not a provider invoice.

Validation: seven cache-cost tests, including the actual LangChain/OpenAI HTTP parsing boundary and mixed lifetimes. Complete suite: 49 tests passed in 13.875 seconds. A live GPT-6 Luna probe returned 1,683 input tokens, including 1,680 writes, and 203 output tokens. Its estimated cost was $0.0002103 input + $0.0001015 output = $0.0003118. No full Charlotte rerun was needed. An independent review found no important defects.

Sources: [OpenAI pricing](https://developers.openai.com/api/docs/pricing), [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).
