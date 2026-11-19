# Bikeshare demand capstone

Repository: [DSC180A-Methodology-6](https://github.com/sfscott-ctrl/DSC180A-Methodology-6)

Implemented and checked **required Exercises 1–5** of the
[DSC methodology assignment](https://dsc-capstone.org/2026-27/assignments/methodology/07-open/).
The first Git commit is the unmodified starter. The remaining history records
the failing feature test, implementation, three source faults and repairs,
the raw-data-copy experiment, self-audit, and report.

Start with [REPORT.md](REPORT.md) and [the fault evidence](docs/SEEDED_FAULTS.md).
The teammate audit is in [docs/AUDIT.md](docs/AUDIT.md). Optional Exercise 6
was not attempted; nothing has been submitted to the course. A final SDK
audit refresh remains pending: three NRP server errors prevented completion.
The successful earlier self-audit is retained and clearly dated in
[docs/SELF_AUDIT.md](docs/SELF_AUDIT.md).

## Reproduce the analysis

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make all
make test
```

`make all` verifies the pinned raw CSV, builds features, and writes
`reports/metrics.json` (with the added feature) and
`reports/metrics_before.json` (without it). `make test` runs 25 tests.
Use `python -m src.train --validation-only` during feature development.
`python -m src.leakage_demo` reproduces the deliberately invalid perfect score.

## Claude Code through NRP

This run used NRP's hosted `qwen3` service through Claude Code. Prompts and
relevant repository content were sent to the authorized NRP endpoint; the
sklearn analysis ran locally. The repository contains no API key.

```bash
bash scripts/claude-nrp.sh
```

Enter your token at the hidden prompt. Full setup and SDK commands are in
[docs/SETUP_NRP.md](docs/SETUP_NRP.md). The custom `/seed-fault` skill packages
the workflow used for the three controlled source faults; the starter's
`/new-feature` skill remains unchanged.

## Optional original Ollama setup

The original `model/` and Makefile targets remain available. Install Ollama
and Claude Code, start `ollama serve`, then run `make model` and
`make check-model`. To use this local server instead of NRP, put the following
nonsecret override in git-ignored `.claude/settings.local.json`:

```json
{
  "model": "bikeshare-coder",
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:11434",
    "ANTHROPIC_AUTH_TOKEN": "ollama",
    "ANTHROPIC_API_KEY": ""
  }
}
```

Then launch `claude` directly; the NRP launcher is for the hosted setup.
The default local model target is `qwen3.5:9b` with a 64k context, as in the
starter. The local-model option was not used or validated in this run.

## Data and safeguards

The checked-in CSV is Molnar's processed mirror of the UCI Bike Sharing
Dataset (Fanaee-T and Gama), not the original UCI daily file. See
`src/config.py` and `reports/data_profile.json` for the schema and differences.
The pipeline runs offline. Its raw SHA256 is pinned and enforced by
`make data` and a test. Edit/Write deny rules alone cannot stop a Bash copy;
the fourth fault demonstrates this distinction in a disposable repository.

Standing constraints are in `CLAUDE.md`; methodological choices and agent
attribution are in `docs/DECISIONS.md` and `REPORT.md`. Observed daily weather
limits the interpretation to a retrospective forecast-proxy evaluation.

## Reproduce validation artifacts without evaluating test

After `make features`, run:

```bash
python -m scripts.reproduce_validation
```

This regenerates both `reports/validation_before.json` (original flat schema)
and `reports/validation_after.json`, scoring only H1 2012. It does not call
the test-scoring path or overwrite the final metrics files.

## Exercise 4: frozen target-transformation study

```bash
# Reproduce all three validation candidates; never scores test:
python -m src.train --target-transform
# Explicitly reproduce the selected model's held-out artifact:
python -m src.train --target-transform --evaluate-test
```

The predeclared plan, validation results, and frozen selection are in
`reports/target_transform_{plan,validation,selection}.json`. The selection
file records the pre-test state. The completed selected-model result is
`reports/target_transformation.json`. It uses exactly the same predictors and
HGB settings as the untransformed comparison. `make all` leaves this separate
study out of `reports/metrics.json`; that file also contains all eight
before/after feature-comparison rows. Replaying a frozen experiment is a
reproducibility check, not a new opportunity to select on test performance.
