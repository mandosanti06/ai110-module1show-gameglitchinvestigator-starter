# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Two phases. First: scan the repo and the running app for bugs and catalog them in
`bugs.md`. Then, in follow-up prompts, I pushed the agent past bug-fixing into
building **new gameplay the starter never had** — turn the fixed-but-bare
single-difficulty guesser into a configurable game with **Difficulty Levels** and
a **Guess History**.

**The new feature claimed for this stretch (not in the starter `app.py`):**

The original starter (`git show 39e8bbe:app.py`, 48 lines) hardcoded a single
`random.randint(1, 100)`, had no `st.session_state`, and kept no record of past
guesses. The agent work added two pieces of genuinely new functionality:

- **Difficulty Levels** — a sidebar selectbox (Easy / Normal / Hard), each with its
  own number range (`get_range_for_difficulty` in `logic_utils.py`) and its own
  attempt limit (`attempt_limit_map` in `app.py:40`). Changing difficulty re-rolls a
  valid in-range secret. None of this existed in the starter's fixed 1–100 game.
- **Guess History** — every accepted guess is recorded in
  `st.session_state.history` and rendered as outcome-colored pills below the input
  (`app.py:256`), and mirrored in the Dev-mode debug panel. The starter discarded
  each guess with no running record.

**Files modified**

- `app.py` — rewritten from the 48-line single-difficulty starter into a stateful
  app: difficulty selector, per-difficulty ranges + attempt limits, scoring,
  Guess History, "New Game" reset, and the RawBlock UI skin.
- `logic_utils.py` — implemented the four helpers the starter left stubbed
  (`get_range_for_difficulty`, `parse_guess`, `check_guess`, `update_score`).
- `bugs.md` — created; 14-bug catalog (code + live findings).
- `tests/test_logic_utils.py`, `tests/test_app_state.py` — created (red-first, then
  green once the bugs were fixed). The suite ended at **31 passed**, later trimmed
  to **27** by the SF9 over-engineering audit (3 duplicate + 1 speculative test
  removed) — see the Linting & Style section.

**Manual corrections made**

- **`check_guess` return contract:** the agent's first refactor copy-pasted
  `app.py`'s tuple return `(outcome, message)`, which failed the string-asserting
  unit tests. I reduced it to a bare outcome string and moved the player-facing
  message into the `HINTS` dict in `app.py` (also written up in `reflection.md` §2).
- **Hard difficulty range:** the agent initially left Hard *narrower* than Normal
  (bug #14), making "Hard" easier; I widened Hard's range in
  `get_range_for_difficulty` so difficulty actually increases.
- **Live verification:** I drove the running app and, for every bug I reproduced by
  hand, confirmed it appeared in `bugs.md` and that the fix held — including the
  attempt-counter init, out-of-range rejection, and New Game state reset.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Decimal input `"12.9"` | create pytests for all the bugs in bugs.md | `test_parse_decimal_is_rejected_not_silently_truncated` | [X] after fix | Decimals should be rejected, not silently truncated to `12`. |
| Guess above the secret | create pytests for all the bugs in bugs.md | `test_check_guess_too_high_says_too_high` | [X] after fix | The hint direction was inverted; a high guess must read "Too High". |
| `100` vs `9` comparison | create pytests for all the bugs in bugs.md | `test_check_guess_uses_numeric_not_lexicographic_comparison` | [X] after fix | `str()` conversion made `"100" < "9"`; comparison must be numeric. |
| Empty / invalid guess | create pytests for all the bugs in bugs.md | `test_empty_guess_does_not_consume_attempt_or_history` | [X] after fix | Attempts were incremented before validation, so junk input cost a turn. |
| New Game after a win | create pytests for all the bugs in bugs.md | `test_new_game_resets_state_after_win` |[X] after fix | New Game left `status`/`score`/`history` stale, locking the player out. |

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

**Linter run (flake8):**

```text
$ flake8 logic_utils.py app.py --max-line-length=120
app.py:23:121: E501 line too long (141 > 120 characters)
app.py:65:121: E501 line too long (139 > 120 characters)
app.py:82:121: E501 line too long (140 > 120 characters)
app.py:85:121: E501 line too long (149 > 120 characters)
app.py:110:121: E501 line too long (141 > 120 characters)
app.py:124:121: E501 line too long (141 > 120 characters)
app.py:141:121: E501 line too long (153 > 120 characters)
```

**Fixed vs. left as-is:**

- **`logic_utils.py` — 0 findings.** The actual game logic is clean; nothing to fix.
- **`app.py` — 7 × E501, all left as-is.** Every flagged line is inside a
  presentation *string literal*, not code flow: the inline SVG icon template
  (line 23), the Google Fonts `@import` URL (line 65), and CSS selector/rule
  strings (lines 82, 85, 110, 124, 141). Wrapping a URL or a BaseWeb selector chain
  across lines hurts readability and risks corrupting the string for no real
  benefit, so these were intentionally left long. No logic-level style issues were
  flagged, so nothing required a code change.
