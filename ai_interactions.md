# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**What did the agent do?**

<!-- List the steps the agent took (files edited, commands run, etc.) -->

**What did you have to verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Decimal input `"12.9"` | create pytests for all the bugs in bugs.md | `test_parse_decimal_is_rejected_not_silently_truncated` | [X] | Decimals should be rejected, not silently truncated to `12`. |
| Guess above the secret | create pytests for all the bugs in bugs.md | `test_guess_too_high` | [X] | The hint direction was inverted; a high guess must read "Too High". |
| Difficulty → range map | add tests for the helpers the ponytail audit flagged untested | `test_range_per_difficulty` | [X] | Easy/Normal/Hard must map to `(1,20)`/`(1,100)`/`(1,50)`. |
| Win score rewards speed | add tests for the helpers the ponytail audit flagged untested | `test_update_score_win_rewards_fewer_attempts_more` | [X] | Earlier wins score higher: `max(10, 100 − 10·attempt)`. |
| Win score floor | add tests for the helpers the ponytail audit flagged untested | `test_update_score_win_reward_floors_at_10` | [X] | Many attempts can't drive the win reward below `10`. |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
/ponytail-audit
```

**Audit output:**

`/ponytail-audit` is an over-engineering audit, not a warning-based linter — a
ranked list of dead flexibility / speculative code, biggest cut first. Whole-tree
scan:

```
shrink: parse_guess returns (ok, value, err); `ok` is just `err is None`. 3-tuple -> 2-tuple (value, err); caller uses `if err`.   [logic_utils.py:7, app.py:208]
yagni:  get_range_for_difficulty `.get(difficulty, (1, 100))` fallback — the selectbox only emits Easy/Normal/Hard, all keyed. -> ranges[difficulty].   [logic_utils.py:4]
yagni:  pct `... if attempt_limit else 0` guard — attempt_limit_map[difficulty] is always >= 5, never 0. Drop the guard.   [app.py:187]
net: ~0 lines, -0 deps possible — 1 contract shrink + 2 dead-flexibility trims; the tree is otherwise lean.
```

**Changes applied:**

All three. The contract shrink (#1) and its single caller changed in lockstep;
trims #2 and #3 are local one-liners:

| # | Change | Files touched |
|---|--------|---------------|
| 1 | `parse_guess` 3-tuple `(ok, value, err)` → 2-tuple `(value, err)`; caller now branches on `if err`; docstring updated | `logic_utils.py`, `app.py` |
| 2 | `get_range_for_difficulty` `.get(difficulty, (1, 100))` → `ranges[difficulty]` | `logic_utils.py` |
| 3 | Dropped the `... if attempt_limit else 0` guard on `pct` | `app.py` |

**Net:** ~-2 lines, -0 dependencies — these are dead-flexibility/contract trims,
not bulk deletions.

**Verification:** `app.py` and `logic_utils.py` compile clean; the only
`parse_guess` call site (`app.py:208`) was confirmed and updated. Suite green:
`11 passed` (`.venv/bin/python -m pytest tests/`).

**Follow-up (correctness, beyond the audit):** closed the flagged coverage gap —
`parse_guess`, `update_score`, and `get_range_for_difficulty` now have tests (see
SF7), taking the suite from 3 to 11. While adding the `parse_guess` test, the
documented "reject decimals" contract ([README](README.md): "no silent decimal
truncation") didn't match the code — `int(float("12.9"))` truncated to `12`.
Fixed it to `int("12.9")`, which rejects decimals outright, locked in with
`test_parse_decimal_is_rejected_not_silently_truncated`.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
