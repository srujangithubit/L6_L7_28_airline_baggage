"""Branch-complete tests for the airline baggage application.

Run from this directory with:
    coverage erase
    coverage run --branch -m pytest -q test_branch_coverage_airline_baggage.py
    coverage report -m airline_baggage.py
"""

import pytest

from airline_baggage import baggage_fee, carry_on_ok, check_in_status


@pytest.mark.parametrize("cabin", ["first", "", None])
def test_unknown_cabin_branch(cabin):
    with pytest.raises(ValueError, match="unknown cabin"):
        baggage_fee(cabin, 10, "domestic", False)


def test_negative_weight_branch():
    with pytest.raises(ValueError, match="invalid weight"):
        baggage_fee("economy", -1, "domestic", False)


@pytest.mark.parametrize(
    "cabin,weight,member,route,expected",
    [
        ("economy", 15, False, "domestic", 0),  # zero excess boundary
        ("premium", 25, True, "domestic", 0),   # member premium allowance
        ("business", 40, True, "domestic", 0),  # business excludes member bonus
        ("economy", 20, True, "domestic", 0),   # member economy allowance
        ("economy", 16, False, "domestic", 20), # domestic route, excess <= 20
        ("economy", 16, False, "international", 45),  # non-domestic route
        ("economy", 36, False, "domestic", 840),       # >20, domestic
        ("economy", 36, False, "international", 2100), # >20, intl surcharge
        ("economy", 36, False, "regional", 1890),      # >20, no intl surcharge
    ],
)
def test_baggage_fee_decision_branches(cabin, weight, member, route, expected):
    assert baggage_fee(cabin, weight, route, member) == expected


@pytest.mark.parametrize(
    "weight,items,infant,expected",
    [
        (5, 1, True, True),   # infant and within item limit
        (5, 2, True, True),   # infant at item boundary
        (5, 3, True, False),  # infant over item limit
        (8, 0, False, False), # non-infant over weight limit
        (7, 1, False, True),  # non-infant at weight and item boundary
        (7, 2, False, False), # non-infant over item limit
    ],
)
def test_carry_on_all_branches(weight, items, infant, expected):
    assert carry_on_ok(weight, items, infant) is expected


@pytest.mark.parametrize(
    "minutes,baggage,international,expected",
    [
        (60, True, False, "open"),
        (59, True, False, "late"),
        (44, True, False, "closed"),
        (45, False, False, "open"),
        (30, False, False, "late"),
        (29, False, False, "closed"),
        (120, True, True, "open"),
        (119, True, True, "late"),
        (104, True, True, "closed"),
        (105, False, True, "open"),
        (90, False, True, "late"),
        (89, False, True, "closed"),
    ],
)
def test_check_in_all_cutoff_branches(minutes, baggage, international, expected):
    assert check_in_status(minutes, baggage, international) == expected
