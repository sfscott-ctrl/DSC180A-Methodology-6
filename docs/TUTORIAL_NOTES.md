# Tutorial observations

The starter implements Steps 1–8. It was committed unchanged, then extended
instead of replacing finished code with a reconstructed tutorial history.
`reports/data_profile.json` records facts measured from the supplied CSV:
728 rows, 2011-01-03 through 2012-12-31, missing 2011-03-10, and weather
counts GOOD 463 / MISTY 245 / BAD 20. The dtype and categorical-value
inventory is included there. Calendar reindexing and seven days of history
leave 714 rows: 348 train, 182 validation, 184 test.

The raw identity `casual + registered == cnt` explains the invalid perfect
score reproduced in `reports/evidence/leakage_demo.txt`. `cnt_2d_bfr` is an
unverified historical lag, not contemporaneous target leakage. A random
split would mix future observations into training and conceal the temporal
growth shift. Features must retain the calendar gap before shifting.

The new feature was requested through Claude Code's `/new-feature` entry
point. Its failing named-date test was committed before implementation.
The hook was exercised through actual Edit tool calls; the event records
retain exit codes and stderr independently of the model's interpretation.
The NRP model sometimes could not distinguish a silent successful hook
from a hook that had not run. The captured hook events resolve that
uncertainty. Manual-hook probing encountered Claude's local permission
checks; these unsuccessful probes are preserved in the feature transcript.

A positive R² is not the same as beating persistence, and a negative R²
is not the same as losing to the training-mean baseline. The final report
keeps both baseline comparisons visible. A histogram gradient booster is
an additive ensemble, so its predictions are not universally guaranteed
to lie within the training-target range. Its piecewise constant response
to inputs nevertheless cannot continue a growing trend outside the feature
ranges it learned; actual range and prediction evidence should accompany
that explanation.

The starter's observed daily weather variables are not available at the
start of the same day. These results describe a retrospective evaluation
using observed weather as a proxy. They do not establish the performance
of a deployable day-ahead system using weather forecasts. Lagged demand is
also updated from actual prior-day outcomes, so evaluation is sequential
one-day-ahead, not a six-month forecast made at one origin.

The follow-up completes Exercises 3–5: see docs/AUDIT.md for the teammate
review and REPORT.md for the target-transformation and deployment arguments.
The selected transformed model uses a historical seven-day demand scale;
the canonical untransformed pipeline remains separate.
