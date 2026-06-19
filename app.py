import random
import streamlit as st

from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)

HINTS = {"Too High": "📉 Go LOWER!", "Too Low": "📈 Go HIGHER!"}


def reset_game(low, high):
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.feedback = None


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Normal", "Hard"], index=1)

attempt_limit = {"Easy": 6, "Normal": 8, "Hard": 5}[difficulty]
low, high = get_range_for_difficulty(difficulty)

if "secret" not in st.session_state:
    reset_game(low, high)
    st.session_state.active_difficulty = difficulty

# bug #8: changing difficulty re-rolls a secret inside the new range
if difficulty != st.session_state.active_difficulty:
    st.session_state.active_difficulty = difficulty
    reset_game(low, high)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    # bug #11: hide the secret until the game is over so it can't be peeked
    if st.session_state.status == "playing":
        st.write("Secret: (hidden until game over)")
    else:
        st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input("Enter your guess:", key="guess_input")

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    reset_game(low, high)
    st.rerun()

if submit and st.session_state.status == "playing":
    guess_int, err = parse_guess(raw_guess)

    if err:
        st.session_state.feedback = ("error", err)
    elif not (low <= guess_int <= high):
        st.session_state.feedback = ("error", f"Guess must be between {low} and {high}.")
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)
        outcome = check_guess(guess_int, st.session_state.secret)
        st.session_state.score = update_score(
            st.session_state.score, outcome, st.session_state.attempts
        )

        if outcome == "Win":
            st.session_state.status = "won"
            st.session_state.feedback = (
                "win",
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}",
            )
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.session_state.feedback = (
                "lost",
                f"Out of attempts! The secret was {st.session_state.secret}. "
                f"Score: {st.session_state.score}",
            )
        else:
            st.session_state.feedback = ("hint", HINTS[outcome])

    # rerun so the info banner and debug panel reflect the new state (bug #4 staleness)
    st.rerun()

fb = st.session_state.feedback
if fb:
    kind, msg = fb
    if kind == "win":
        st.success(msg)
    elif kind in ("error", "lost"):
        st.error(msg)
    elif kind == "hint" and show_hint:
        st.warning(msg)

if st.session_state.status != "playing":
    st.caption("Click New Game 🔁 to play again.")

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
