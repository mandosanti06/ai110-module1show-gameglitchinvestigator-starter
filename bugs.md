# Bug Report — Game Glitch Investigator

Bugs found in the broken "GameGenie" game and how each was fixed. All fixes are
covered by `pytest` (11 passing — see [README](README.md)).

| # | Bug | Broken behavior | Fix |
|---|-----|-----------------|-----|
| 1 | Secret regenerated every rerun | `secret_number = random.randint(1, 100)` ran at module level, so the number changed on every guess — unwinnable | Stored in `st.session_state.secret`, set once per round ([app.py:153](app.py#L153)) |
| 2 | Hints inverted | A too-high guess said "Go HIGHER", a too-low one said "Go LOWER" | `check_guess` returns the correct direction ([logic_utils.py:21](logic_utils.py#L21)) |
| 3 | `check_guess` unimplemented | Returned the literal `"Not Implemented"`, so tests failed | Returns `"Win"`/`"Too High"`/`"Too Low"` ([logic_utils.py:21](logic_utils.py#L21)) |
| 4 | Decimals silently truncated | `int(float("12.9"))` → `12` with no warning | `int(raw)` rejects non-integers ([logic_utils.py:16](logic_utils.py#L16)) |
| 5 | Difficulty range not honored | New Game always rolled `1–100`; a dead `.get(..., (1, 100))` fallback masked bad keys | Rolls `random.randint(low, high)`; range keyed directly ([logic_utils.py:4](logic_utils.py#L4), [app.py:153](app.py#L153)) |
| 6 | Scoring broken | Off-by-one win reward, asymmetric +5/−5, score never reset between games | `max(10, 100 − 10·attempts)` on win, −5 per wrong guess, reset in `new_game_state()` ([logic_utils.py:32](logic_utils.py#L32)) |

Tests: [tests/test_game_logic.py](tests/test_game_logic.py).
