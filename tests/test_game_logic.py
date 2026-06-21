from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)

# ---- check_guess -----------------------------------------------------------

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"

# ---- get_range_for_difficulty ----------------------------------------------

def test_range_per_difficulty():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 100)
    assert get_range_for_difficulty("Hard") == (1, 50)

# ---- parse_guess -----------------------------------------------------------

def test_parse_valid_integer():
    assert parse_guess("7") == (7, None)

def test_parse_empty_is_rejected():
    guess, err = parse_guess("")
    assert guess is None and err

def test_parse_non_number_is_rejected():
    guess, err = parse_guess("abc")
    assert guess is None and err

def test_parse_decimal_is_rejected_not_silently_truncated():
    # "12.9" must NOT become 12 — reject it instead of truncating
    guess, err = parse_guess("12.9")
    assert guess is None and err

# ---- update_score ----------------------------------------------------------

def test_update_score_wrong_guess_loses_5():
    assert update_score(100, "Too High", 3) == 95

def test_update_score_win_rewards_fewer_attempts_more():
    assert update_score(0, "Win", 1) == 90   # max(10, 100 - 10)
    assert update_score(0, "Win", 8) == 20   # max(10, 100 - 80)

def test_update_score_win_reward_floors_at_10():
    assert update_score(0, "Win", 20) == 10  # max(10, negative) -> 10
