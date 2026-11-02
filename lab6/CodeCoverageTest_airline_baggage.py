import pytest

from airline_baggage import baggage_fee, carry_on_ok, check_in_status


# Existing starter scenarios.
def test_within_allowance():
    assert baggage_fee("economy", 10, "domestic", False) == 0


def test_carry_on_ok():
    assert carry_on_ok(5, 1, False) is True


# baggage_fee: validation, cabin allowance, membership and route/rate paths.
@pytest.mark.parametrize("cabin", ["first", "", None])
def test_unknown_cabin_raises(cabin):
    with pytest.raises(ValueError, match="unknown cabin"):
        baggage_fee(cabin, 10, "domestic", False)


def test_negative_weight_raises():
    with pytest.raises(ValueError, match="invalid weight"):
        baggage_fee("economy", -0.1, "domestic", False)


@pytest.mark.parametrize(
    "cabin,weight,member,expected",
    [
        ("economy", 15, False, 0),
        ("premium", 25, False, 0),
        ("business", 40, False, 0),
        ("economy", 20, True, 0),
        ("premium", 35, True, 0),
        # Membership does not increase business-class allowance.
        ("business", 40, True, 0),
    ],
)
def test_allowance_boundaries(cabin, weight, member, expected):
    assert baggage_fee(cabin, weight, "domestic", member) == expected


def test_domestic_excess_up_to_twenty_kg_uses_base_rate():
    assert baggage_fee("economy", 20, "domestic", False) == 5 * 20


def test_non_domestic_route_uses_international_base_rate():
    # The application treats every non-domestic route as the higher-rate route.
    assert baggage_fee("economy", 16, "international", False) == 45


def test_large_domestic_excess_doubles_rate():
    assert baggage_fee("economy", 36, "domestic", False) == 21 * 40


def test_large_international_excess_doubles_and_adds_surcharge():
    assert baggage_fee("economy", 36, "international", False) == 21 * 100


def test_large_excess_on_other_route_doubles_without_international_surcharge():
    assert baggage_fee("economy", 36, "regional", False) == 21 * 90


# carry_on_ok: infant allowance, weight limit and item-count limit.
@pytest.mark.parametrize("weight,items,expected", [(0, 0, True), (20, 2, True), (5, 3, False)])
def test_infant_carry_on_limit(weight, items, expected):
    assert carry_on_ok(weight, items, True) is expected


def test_non_infant_weight_over_seven_is_rejected():
    assert carry_on_ok(7.01, 0, False) is False


def test_non_infant_weight_at_seven_and_one_item_is_allowed():
    assert carry_on_ok(7, 1, False) is True


def test_non_infant_more_than_one_item_is_rejected():
    assert carry_on_ok(7, 2, False) is False


# check_in_status: both cutoff calculations and all three outcomes.
@pytest.mark.parametrize(
    "minutes,has_baggage,international,expected",
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
def test_check_in_status_cutoff_boundaries(minutes, has_baggage, international, expected):
    assert check_in_status(minutes, has_baggage, international) == expected
