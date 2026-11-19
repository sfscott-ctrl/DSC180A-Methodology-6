---
name: seed-fault
description: Run one controlled mutation experiment, record test and hook failures, then restore the original source. Use for the assignment fault exercise.
allowed-tools: Read, Edit, Bash(make:*), Bash(python -m pytest:*), Bash(git diff:*)
---

# Fault experiment: $ARGUMENTS

Use only the source mutation named in the argument. Read and preserve the
original text first. Never weaken a test to repair the experiment.

1. Establish a green `make test`. Record the exact proposed source diff.
2. Seed one fault with **Edit**, not Bash: the configured PostToolUse hook
   must run on the edit. Save the actual hook stderr and exit status from
   the tool result; do not reconstruct or invent them.
3. Run `make test` while the fault exists. Keep its full red output and
   identify the failing assertion. If it stays green, stop and report
   the missing coverage before claiming detection.
4. Repair the source with Edit, run `make test`, and confirm green.
   Count repair attempts from the first red run, separately from assistant
   messages/tool calls. Report both when the transcript makes them available.
5. Return the exact diff, raw red output, raw hook stderr, green result,
   and repair count for inclusion in `docs/SEEDED_FAULTS.md`. The driver
   saves the transcript and commits this experiment separately.

The Bash/raw-data bypass is a separate controlled experiment. Use a
throwaway copy of the repository for it; never corrupt the deliverable's
raw CSV. A Bash edit is outside this Edit/Write hook's matcher.
