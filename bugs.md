# Bug Report — Game Glitch Investigator

Scanned `app.py`, `logic_utils.py`, and `tests/`, and drove the running
Streamlit app (`localhost:8533`) to confirm behavior. Tags below:
**[live]** = reproduced in the running app, **[code]** = confirmed by reading.

---

## 1. Tests fail: `logic_utils.py` is still stubbed AND the contract doesn't match `app.py` [live]

- **Where:** `logic_utils.py:1-26`, `tests/test_game_logic.py`
- **Evidence:** `pytest -q` → 3 failed, all `NotImplementedError`.
- **Deeper bug:** The tests expect `check_guess(...)` to return a bare string
  (`assert check_guess(50,50) == "Win"`), but `app.py`'s `check_guess` returns a
  **tuple** `(outcome, message)`. A copy-paste refactor into `logic_utils.py`
  still fails the tests — you must reconcile the return type with the caller at
  `app.py:163` (`outcome, message = check_guess(...)`).
- **Impact:** Logic is duplicated across two files and the test contract is
  inconsistent with the implementation.

## 2. Hint directions are inverted [live]

- **Where:** `app.py:37-40`
- **Evidence:** Secret `86`, guessed `90` → app showed **"📈 Go HIGHER!"**.
- **Expected:** guess above secret → tell player to go LOWER; below → HIGHER.
- Also note the messages are mislabeled: the `Too High` branch returns the
  "Go HIGHER" string and vice-versa.

## 3. Secret is stringified on even attempts → broken comparisons [code]

- **Where:** `app.py:158-161`
- **Evidence:** On even attempts, `secret = str(...)` before `check_guess`.
  `check_guess(int, str)` raises `TypeError` and falls into a string-comparison
  fallback, so e.g. `"100" < "9"`. A correct equal guess on an even attempt
  (`86 == "86"` is `False` in Python) only "wins" via the accidental `str()`
  fallback — fragile and wrong for mixed-width numbers.

## 4. Attempt counter starts at 1; debug panel shows stale values [live]

- **Where:** `app.py:95-96` (init `= 1`), `app.py:135` (New Game `= 0`), `app.py:111`, `app.py:114-119`
- **Evidence:** Fresh Normal game (8 allowed) showed **"Attempts left: 7"**.
  Debug "Attempts:" stayed at the pre-submit value because the panel renders
  (line 114) before the submit handler increments (line 148).
- **Inconsistency:** init uses `1`, New Game uses `0` — after New Game the app
  correctly showed "Attempts left: 8". Initial load should also start at 0.

## 5. Invalid/empty guesses consume attempts and pollute history [live]

- **Where:** `app.py:147-154`
- **Evidence:** Two empty submits → attempts went 1→2→3 and `History` became
  `["", "", ...]`. `attempts += 1` (line 148) runs before `parse_guess`, and the
  raw invalid value is appended to history (line 153).

## 6. New Game doesn't reset game state [live]

- **Where:** `app.py:134-138`
- **Evidence:** After New Game, secret + attempts reset but **History was NOT
  cleared** (`["", "", 90, 90]` persisted). Code never resets `status`, `score`,
  or `history`.
- **Worse:** if the player has won, `status` stays `"won"`, so the next render
  hits `app.py:140-145` and shows *"You already won. Start a new game…"* then
  `st.stop()` — the game is unplayable after a win until the session restarts.

## 7. New Game ignores the selected difficulty range [code]

- **Where:** `app.py:136`
- **Evidence:** Always `random.randint(1, 100)` instead of `random.randint(low, high)`.
- **Impact:** In Easy (1–20) or Hard (1–50) the secret can be outside the
  advertised range.

## 8. Changing difficulty never re-rolls / revalidates the secret [code]

- **Where:** `app.py:92-93`
- **Evidence:** Secret is set only `if "secret" not in st.session_state`, so it's
  fixed for the whole session. Switching difficulty changes the displayed range
  but leaves the old secret (e.g. secret `41` while range shows "1 to 20").

## 9. Main prompt is hardcoded to "1 and 100" [code]

- **Where:** `app.py:109-111`
- **Evidence:** The `st.info` text hardcodes *"between 1 and 100"* while the
  sidebar uses `low`/`high`. In Easy/Hard the prompt contradicts the sidebar
  ("Range: 1 to 20").

## 10. Scoring is nonsensical and not isolated per game [live/code]

- **Where:** `app.py:50-65`, `app.py:135-137`
- **Evidence:** `update_score` uses `attempt_number + 1` (line 52), so a
  first-attempt win scores `100 - 10*(2+1) = 70` instead of ~100. `Too High`
  gives `+5` on even attempts but `-5` on odd (line 57-60), while `Too Low` is
  always `-5` — asymmetric and arbitrary. New Game never resets `score`, so it
  carries across games.

## 11. Debug panel reveals the secret [code]

- **Where:** `app.py:114-119`
- **Evidence:** `Secret: <n>` is shown in the expander, making the game trivial.
  (Intentional for the lesson, but a real bug for a playable game.)

## 12. `parse_guess` silently truncates decimals [code]

- **Where:** `app.py:21-25`
- **Evidence:** Input with `.` → `int(float(raw))`, so `12.9` → `12` with no
  warning. Either reject non-integers or round explicitly.

## 13. Guesses aren't validated against the active range [code]

- **Where:** `app.py:150-156`
- **Evidence:** Any parsed integer is accepted; no `low <= guess <= high` check,
  so out-of-range guesses are recorded.

## 14. "Hard" has a narrower range than "Normal" [code]

- **Where:** `app.py:4-11`, `app.py:80-84`
- **Evidence:** Easy=1–20, Normal=1–**100**, Hard=1–**50**. By range, "Hard"
  is easier to guess than "Normal" (it only gets fewer attempts: 5 vs 8). The
  difficulty ordering is inconsistent.

---

### How to reproduce the live findings

```batch
.venv/bin/python -m streamlit run app.py
# open Developer Debug Info to read the secret, then submit guesses
.venv/bin/python -m pytest -q   # 3 failures
```
