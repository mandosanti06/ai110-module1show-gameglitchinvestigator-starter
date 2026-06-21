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

I used AI to help find and fix the bugs. Some suggestions were right, like using
session state for the secret. One was off and needed fixing.

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
