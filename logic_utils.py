def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    ranges = {"Easy": (1, 20), "Normal": (1, 100), "Hard": (1, 50)}
    return ranges.get(difficulty, (1, 100))


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if not raw:
        return False, None, "Enter a guess."
    try:
        return True, int(float(raw)), None
    except ValueError:
        return False, None, "That is not a number."


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win"
    return "Too High" if guess > secret else "Too Low"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        return current_score + max(10, 100 - 10 * attempt_number)
    return current_score - 5  # wrong guess
