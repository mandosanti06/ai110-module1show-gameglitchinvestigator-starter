# 💭 Reflection: Game Glitch Investigator

## 1. What was broken when you started?

The game was unwinnable. The secret kept changing, the hints were backwards, and
the tests didn't pass.

**Bug Reproduction Log**

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Same guess twice | Secret stays the same | Secret changes each click | (none) |
| Guess above the secret | Hint: go lower | Hint: go higher | (none) |
| `pytest tests/` | Tests pass | Tests failed | `AssertionError` |

---

## 2. How did you use AI as a teammate?

I treated the AI as a pair-debugger whose suggestions I verified rather than
trusted on sight.

**A suggestion that was right.** For the "secret changes on every guess" bug
(bugs.md #1), the AI's advice was to *stop generating the secret at module level
(`secret_number = random.randint(1, 100)`) and store it in `st.session_state`
instead, set once per round.* That was correct, and I could explain why: Streamlit
re-runs the entire script top-to-bottom on every widget interaction, so any plain
module-level variable is re-initialized each rerun — the `randint` call literally
re-rolled the secret on every click. Session state is the one place a value
survives reruns. The fix landed in `new_game_state()` (`app.py:152`) and is pinned
down by `tests/test_app_state.py`, which submits the same guess twice and asserts
the secret is unchanged.

**A suggestion that was wrong.** While moving `check_guess` into `logic_utils.py`
(bugs.md #1, "the contract doesn't match"), the AI first suggested a straight
copy-paste of `app.py`'s version, which returned a **tuple** `(outcome, message)`.
That looked reasonable but still failed `pytest`, because the unit tests assert a
**bare string** (`check_guess(50, 50) == "Win"`). The suggestion was wrong because
it treated the refactor as pure relocation and ignored that the function had two
different callers expecting two different return shapes. The real fix was to make
`check_guess` return just the outcome string (`"Win"`/`"Too High"`/`"Too Low"`)
and move the player-facing message mapping into the `HINTS` dict in `app.py`
(`app.py:14`). Tests passing — not the AI's confidence — is what told me which
version was correct.

---

## 3. Debugging and testing your fixes

I trusted a fix once its test passed and the game behaved right. Running pytest
showed me which parts were still broken. AI helped write a few of the tests.

---

## 4. What did you learn about Streamlit and state?

The script reruns on every interaction, so normal variables reset each time.
Session state is what keeps values around.

---

## 5. Looking ahead: your developer habits

I want to keep testing as I go. Next time I'd check AI code more carefully before
trusting it, since it can run fine and still be wrong.

---

## 6. Conclusion

This project turned a deliberately broken, AI-"perfect" guessing game into one
that actually works, and along the way it hit every goal it set out to teach.

- **Found syntax, logic, and runtime bugs in AI-generated code.** The 14-bug
  catalog in `bugs.md` spans all three: stubbed/duplicated logic that broke `pytest`
  (a *logic/contract* bug), `int < str` comparisons from stringifying the secret on
  even attempts (a *runtime* `TypeError`), and inverted "Higher/Lower" hints (a
  *logic* bug that ran fine and still misled the player).

- **Used AI critically — propose, test, verify — not on faith.** Every AI fix had
  to clear a test before I accepted it. AI proposed the `st.session_state` fix for
  the re-rolling secret and I verified *why* it was right; it also proposed a
  copy-paste `check_guess` refactor that I rejected once the tests stayed red.
  "It runs" was never the bar; "the test passes and I can explain why" was.

- **Applied readable, testable fixes with AI-generated `pytest` cases.** The logic
  moved into `logic_utils.py` behind four small, named helpers, and the suite
  (`test_logic_utils.py` + `test_app_state.py`, **27 passed**) pins down each fixed
  bug — including a state test that submits the same guess twice to prove the secret
  no longer changes.

- **Exercised human judgment over AI plans — accept, modify, reject.** I *accepted*
  the session-state fix, *modified* `check_guess` to return a bare string instead of
  the AI's tuple, and *rejected* both a difficulty range that made "Hard" easier
  than "Normal" (bug #14) and the linter/audit suggestions that didn't earn their
  keep. The tools sped up the work; the decisions stayed mine.

The lasting habit: treat AI as a fast, confident, fallible teammate — let it draft,
but make the test suite and my own reasoning be what decides whether code ships.
