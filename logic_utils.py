def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    ranges = {
        "Easy": (1, 20),
        "Normal": (1, 100),
        "Hard": (1, 200),  # bug #14: Hard must be at least as wide as Normal
    }
    return ranges[difficulty]  # difficulty is selectbox-constrained to these keys


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (guess_int: int | None, error_message: str | None) — error set on failure.
    """
    if not raw:  # None or ""
        return None, "Enter a guess."
    try:
        value = int(raw)  # bug #12: int() rejects "12.9" instead of truncating it
    except (ValueError, TypeError):
        return None, "That is not a whole number."
    return value, None


def check_guess(guess, secret):
    """Compare guess to secret, return outcome string: 'Win' | 'Too High' | 'Too Low'."""
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and 1-based attempt number."""
    if outcome == "Win":
        return current_score + max(10, 100 - 10 * (attempt_number - 1))
    return current_score - 5  # Too High / Too Low — the only other outcomes
