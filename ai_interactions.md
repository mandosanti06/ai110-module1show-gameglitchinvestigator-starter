# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Scan this repo for bugs and create a bugs.md file with the list of bugs. Also use the app to find the bugs in app.

**What did the agent do?**

The agent identified syntax and logic bugs and started adding them to a bugs.md file, then ran the app in its preview tab and added the bugs found in the run time. In follow-up prompts I had it go further: generate pytest tests for every bug in bugs.md (red first), then fix all 14 bugs by moving the logic into `logic_utils.py` and rewriting `app.py`. The full suite ended green (**31 passed**).

**What did you have to verify or fix manually?**

I tested the app manually, and for every bug I found, I checked if it was found by the agent.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Decimal input `"12.9"` | create pytests for all the bugs in bugs.md | `test_parse_decimal_is_rejected_not_silently_truncated` | ✅ after fix | Decimals should be rejected, not silently truncated to `12`. |
| Guess above the secret | create pytests for all the bugs in bugs.md | `test_check_guess_too_high_says_too_high` | ✅ after fix | The hint direction was inverted; a high guess must read "Too High". |
| `100` vs `9` comparison | create pytests for all the bugs in bugs.md | `test_check_guess_uses_numeric_not_lexicographic_comparison` | ✅ after fix | `str()` conversion made `"100" < "9"`; comparison must be numeric. |
| Empty / invalid guess | create pytests for all the bugs in bugs.md | `test_empty_guess_does_not_consume_attempt_or_history` | ✅ after fix | Attempts were incremented before validation, so junk input cost a turn. |
| New Game after a win | create pytests for all the bugs in bugs.md | `test_new_game_resets_state_after_win` | ✅ after fix | New Game left `status`/`score`/`history` stale, locking the player out. |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```txt
/ponytail:ponytail-audit — repo-wide scan for over-engineering (dead code,
unused dependencies, reinvented stdlib, speculative flexibility). Ranked
findings, report-only.
```

**Audit findings (ranked, biggest cut first):**

| # | Tag | What to cut | Replacement | Location |
|---|-----|-------------|-------------|----------|
| 1 | delete | `tests/test_game_logic.py` — its 3 tests duplicate `test_check_guess_win/too_high/too_low` | nothing | `tests/test_game_logic.py` |
| 2 | delete | `altair<5` pin — no charts, no `import altair`; Streamlit ships altair transitively | drop the line | `requirements.txt` |
| 3 | yagni | `get_range_for_difficulty`'s `.get(difficulty, (1,100))` fallback for a 3-key selectbox | `return ranges[difficulty]` (+ drop `test_range_unknown`) | `logic_utils.py:8` |
| 4 | shrink | `parse_guess` returns `(ok, value, err)`; `ok` is just `err is None` (three signals for two states) | return `(value, err)` | `logic_utils.py:11` |
| 5 | delete | `update_score`'s final `return current_score` — `outcome` is always Win/Too High/Too Low, branch never fires | drop the dead branch | `logic_utils.py:41` |

**net: -24 lines, -1 dependency possible.**

**Changes applied:**

Applied the safe trio — #1, #2, #5:

- **#1** Deleted `tests/test_game_logic.py` (3 tests duplicated `test_logic_utils.py`).
- **#2** Removed the `altair<5` pin from `requirements.txt` (unused; Streamlit ships altair transitively).
- **#5** Collapsed `update_score`'s dead `return current_score` and the redundant `if outcome in (...)` guard into a single `return current_score - 5` fallback.

Then applied the contract-touching pair — #3 and #4 — across source + tests in lockstep:

- **#3** Replaced `get_range_for_difficulty`'s `.get(difficulty, (1,100))` with `ranges[difficulty]` (the selectbox only emits the 3 known keys); dropped the now-invalid `test_range_unknown_falls_back_to_a_valid_range`.
- **#4** Shrank `parse_guess` from `(ok, value, err)` to `(value, err)` — `ok` was just `err is None`. Updated the unpack at `app.py:80` (`if err:`) and all five `parse_guess` assertions in `test_logic_utils.py`.

Net applied (all five): **~-23 lines, -1 dependency.**

**Suite after:** `27 passed` (31 → 28 after dropping 3 duplicate tests → 27
after retiring the speculative unknown-key test). No real coverage lost.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

|                          | Model A | Model B |
|--------------------------|---------|---------|
|      **Model name**      |         |         |
|   **Response summary**   |         |         |
|    **More Pythonic?**    |         |         |
| **Clearer explanation?** |         |         |

**Which did you prefer and why?**

<!-- Your conclusion -->
