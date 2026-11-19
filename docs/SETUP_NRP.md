# Reproduce this partial assignment

Scope: tutorial and Part 4 self-audit, then Part 5 Exercises 1 and 2.
Exercises 3–5 are intentionally left for later. No repository was published
or submitted to the course.

## Python pipeline

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make all
make test
```

The checked-in raw CSV permits an offline pipeline. `reports/metrics.json`
is the final feature set; `reports/metrics_before.json` is the same pipeline
with `cnt_roll_3` removed. Both regenerate with `make all`.
Use `python -m src.train --validation-only` while making decisions.

## NRP in Claude Code

Install Claude Code using its official installation instructions, then run:

```bash
bash scripts/claude-nrp.sh
```

Paste the course token at the hidden prompt. The script keeps it in the
process environment. Do not paste it into settings, Markdown, Git, or a
shell command saved in history. The project retains the starter's hook and
permission rules while using the documented NRP Anthropic endpoint.
The selected service model is `qwen3`; its backend may change over time.

For the SDK audit:

```bash
bash scripts/claude-nrp.sh --audit . --out reports/audit.jsonl --concurrency 1
```

For the exercised workflows inside Claude Code:

```text
/new-feature cnt_roll_3
/seed-fault add casual to feature_columns
```

Only run a deliberate fault experiment in a disposable/clean checkout,
and restore the original source after recording red tests. The delivery
includes the actual recorded runs; they need not be rerun for reading.

Sources: [assignment](https://dsc-capstone.org/2026-27/assignments/methodology/07-open/),
[NRP API](https://nrp.ai/llmtoken/),
[NRP Claude configuration](https://nrp.ai/documentation/userdocs/ai/llm-managed/client-configs/#claude-code).

## Reproduce validation artifacts without evaluating test

After `make features`, run:

```bash
python -m scripts.reproduce_validation
```

This regenerates both `reports/validation_before.json` (original flat schema)
and `reports/validation_after.json`, scoring only H1 2012. It does not call
the test-scoring path or overwrite the final metrics files.
