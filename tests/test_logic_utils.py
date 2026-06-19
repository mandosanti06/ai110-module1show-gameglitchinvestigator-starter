"""
Unit tests for the pure game logic, targeting `logic_utils.py`.

These encode the CORRECT behavior the refactored functions must satisfy.
They are RED until the logic is moved into `logic_utils.py` and the bugs in
`bugs.md` are fixed -- that's the point (red -> green). Each test name maps to
a bug number in bugs.md.
"""
import pytest
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)


# --- get_range_for_difficulty (bugs #7, #8, #9, #14) ---

def test_range_easy():
    assert get_range_for_difficulty("Easy") == (1, 20)

def test_range_normal():
    assert get_range_for_difficulty("Normal") == (1, 100)

def test_range_hard():
    # bug #14: "Hard" must not be easier (narrower) than "Normal".
    low, high = get_range_for_difficulty("Hard")
    assert low == 1
    assert high >= get_range_for_difficulty("Normal")[1]


# --- parse_guess (bugs #1-contract, #12) ---

def test_parse_valid_integer():
    assert parse_guess("42") == (42, None)

def test_parse_empty_is_rejected():
    value, err = parse_guess("")
    assert value is None and err

def test_parse_none_is_rejected():
    value, err = parse_guess(None)
    assert value is None and err

def test_parse_non_numeric_is_rejected():
    value, err = parse_guess("abc")
    assert value is None and err

def test_parse_decimal_is_rejected_not_silently_truncated():
    # bug #12: "12.9" must NOT silently become 12.
    value, err = parse_guess("12.9")
    assert value is None, "decimals should be rejected, not truncated to int"


# --- check_guess (bugs #1, #2, #3) ---

def test_check_guess_returns_a_string_outcome():
    # bug #1: tests expect a bare string, app.py returns a tuple.
    assert isinstance(check_guess(50, 50), str)

def test_check_guess_win():
    assert check_guess(50, 50) == "Win"

def test_check_guess_too_high_says_too_high():
    # bug #2: a guess above the secret is "Too High".
    assert check_guess(60, 50) == "Too High"

def test_check_guess_too_low_says_too_low():
    # bug #2: a guess below the secret is "Too Low".
    assert check_guess(40, 50) == "Too Low"

def test_check_guess_uses_numeric_not_lexicographic_comparison():
    # bug #3: 100 > 9 numerically; string compare would call "100" < "9".
    assert check_guess(100, 9) == "Too High"
    assert check_guess(9, 100) == "Too Low"


# --- update_score (bug #10) ---

def test_winning_earns_positive_points():
    assert update_score(0, "Win", 1) > 0

def test_first_attempt_win_is_near_maximum():
    # bug #10: the `attempt_number + 1` offset makes a 1st-try win score ~70.
    assert update_score(0, "Win", 1) >= 90

def test_earlier_win_scores_at_least_as_high_as_a_later_win():
    assert update_score(0, "Win", 1) >= update_score(0, "Win", 5)

def test_wrong_guess_never_increases_score():
    # bug #10: "Too High" on an even attempt currently ADDS +5.
    for n in range(1, 7):
        assert update_score(0, "Too High", n) <= 0
        assert update_score(0, "Too Low", n) <= 0

def test_too_high_and_too_low_penalize_symmetrically():
    # bug #10: penalty must not depend on attempt parity / direction.
    assert update_score(0, "Too High", 2) == update_score(0, "Too Low", 2)
    assert update_score(0, "Too High", 2) == update_score(0, "Too High", 3)
