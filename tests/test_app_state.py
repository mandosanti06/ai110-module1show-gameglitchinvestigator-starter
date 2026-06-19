"""
App/state-wiring tests for the bugs in bugs.md that live in app.py's Streamlit
wiring (not the pure logic functions -- those are covered by test_logic_utils.py).

Driven with streamlit.testing.v1.AppTest. Each test asserts the CORRECT behavior,
so they are RED against the current buggy app.py and turn GREEN once fixed.
Test names map to bug numbers in bugs.md.
"""
from streamlit.testing.v1 import AppTest


def fresh():
    return AppTest.from_file("app.py").run()


# --- bug #4: attempt counter starts at 1 instead of 0 ---

def test_fresh_game_starts_with_full_attempts():
    at = fresh()
    assert at.session_state["attempts"] == 0
    # Normal mode allows 8 attempts; a fresh game must advertise all of them.
    assert "Attempts left: 8" in at.info[0].value


# --- bug #5: invalid guesses consume attempts and pollute history ---

def test_empty_guess_does_not_consume_attempt_or_history():
    at = fresh()
    before = at.session_state["attempts"]
    at.text_input[0].set_value("").run()
    at.button[0].click().run()  # Submit
    assert at.session_state["attempts"] == before
    assert at.session_state["history"] == []


def test_nonnumeric_guess_does_not_consume_attempt_or_history():
    at = fresh()
    before = at.session_state["attempts"]
    at.text_input[0].set_value("abc").run()
    at.button[0].click().run()
    assert at.session_state["attempts"] == before
    assert at.session_state["history"] == []


# --- bug #6: New Game doesn't reset status/score/history ---

def test_new_game_resets_state_after_win():
    at = fresh()
    at.text_input[0].set_value(str(at.session_state["secret"])).run()
    at.button[0].click().run()  # Submit winning guess
    assert at.session_state["status"] == "won"  # sanity: we actually won

    at.button[1].click().run()  # New Game
    assert at.session_state["status"] == "playing"
    assert at.session_state["score"] == 0
    assert at.session_state["history"] == []


# --- bug #7: New Game ignores the selected difficulty range ---

def test_new_game_secret_within_difficulty_range():
    at = fresh()
    at.selectbox[0].set_value("Easy").run()  # Easy = 1..20
    # ponytail: 25 redraws; randint(1,100) escapes 1..20 ~80% of the time, so
    # this is deterministic in practice. Make it exact with a seed if it flakes.
    for _ in range(25):
        at.button[1].click().run()
        assert 1 <= at.session_state["secret"] <= 20


# --- bug #8: changing difficulty never re-rolls / revalidates the secret ---

def test_changing_difficulty_revalidates_secret():
    at = fresh()
    at.session_state["secret"] = 99  # out of Easy's 1..20 range
    at.selectbox[0].set_value("Easy").run()
    assert at.session_state["secret"] <= 20


# --- bug #9: main prompt is hardcoded to "1 and 100" ---

def test_prompt_reflects_selected_range():
    at = fresh()
    at.selectbox[0].set_value("Easy").run()
    prompt = at.info[0].value
    assert "20" in prompt
    assert "100" not in prompt


# --- bug #11: debug panel reveals the secret during play ---

def test_secret_hidden_during_play():
    at = fresh()
    assert at.session_state["status"] == "playing"
    reveal = f"Secret: `{at.session_state['secret']}`"
    assert not any(reveal in (m.value or "") for m in at.markdown)


# --- bug #13: guesses aren't validated against the active range ---

def test_out_of_range_guess_is_rejected():
    at = fresh()  # Normal = 1..100
    at.text_input[0].set_value("999").run()
    at.button[0].click().run()
    assert 999 not in at.session_state["history"]
