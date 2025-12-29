# tests/test_budget_model.py
import uuid
import pytest
from decimal import Decimal

from pocket_ledger.models.budget import Budget, BudgetPeriod

def test_budget_threshold_validation_ok():
    b = Budget(user_id=uuid.uuid4(), period=BudgetPeriod.MONTHLY, limit_amount=Decimal("100"), threshold_percent=80)
    assert b.threshold_percent == 80

def test_budget_threshold_validation_invalid_raises():
    with pytest.raises(Exception):
        Budget(user_id=uuid.uuid4(), period=BudgetPeriod.MONTHLY, limit_amount=Decimal("100"), threshold_percent=120)

def test_is_exceeded_boundary():
    b = Budget(user_id=uuid.uuid4(), period=BudgetPeriod.MONTHLY, limit_amount=Decimal("100"), threshold_percent=80)
    assert b.is_exceeded(Decimal("100")) is False
    assert b.is_exceeded(Decimal("100.01")) is True

def test_is_threshold_reached_boundary():
    b = Budget(user_id=uuid.uuid4(), period=BudgetPeriod.MONTHLY, limit_amount=Decimal("100"), threshold_percent=80)
    assert b.is_threshold_reached(Decimal("79.99")) is False
    assert b.is_threshold_reached(Decimal("80")) is True

def test_remaining_amount_can_be_negative():
    b = Budget(user_id=uuid.uuid4(), period=BudgetPeriod.MONTHLY, limit_amount=Decimal("100"), threshold_percent=80)
    assert b.get_remaining_amount(Decimal("30")) == Decimal("70")
    assert b.get_remaining_amount(Decimal("120")) == Decimal("-20")

def test_usage_percentage():
    b = Budget(user_id=uuid.uuid4(), period=BudgetPeriod.MONTHLY, limit_amount=Decimal("200"), threshold_percent=80)
    assert abs(b.get_usage_percentage(Decimal("50")) - 25.0) < 1e-9

def test_update_limit_and_threshold():
    b = Budget(user_id=uuid.uuid4(), period=BudgetPeriod.MONTHLY, limit_amount=Decimal("100"), threshold_percent=80)
    b.update_limit(Decimal("300"))
    assert b.limit_amount == Decimal("300")
    b.update_threshold(90)
    assert b.threshold_percent == 90

def test_activate_deactivate():
    b = Budget(user_id=uuid.uuid4(), period=BudgetPeriod.MONTHLY, limit_amount=Decimal("100"), threshold_percent=80)
    b.deactivate()
    assert b.is_active is False
    b.activate()
    assert b.is_active is True

def test_to_dict_from_dict_roundtrip():
    b1 = Budget(
        user_id=uuid.uuid4(),
        period=BudgetPeriod.WEEKLY,
        limit_amount=Decimal("123.45"),
        threshold_percent=70,
        category_id=None,
        is_active=True
    )
    d = b1.to_dict()
    b2 = Budget.from_dict(d)
    assert b1.budget_id == b2.budget_id
    assert b2.period == BudgetPeriod.WEEKLY
    assert b2.limit_amount == Decimal("123.45")
    assert b2.threshold_percent == 70
