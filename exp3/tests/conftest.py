# tests/conftest.py
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中，便于 import pocket_ledger
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import uuid
import pytest
from datetime import datetime
from decimal import Decimal

from pocket_ledger.database.database import Database
from pocket_ledger.models.category import Category, CategoryType
from pocket_ledger.models.entry import Entry
from pocket_ledger.models.tag import Tag
from pocket_ledger.models.budget import Budget, BudgetPeriod

@pytest.fixture()
def db(tmp_path):
    db_path = tmp_path / "test_db.json"
    return Database(str(db_path))

@pytest.fixture()
def user_ids():
    return uuid.uuid4(), uuid.uuid4()

@pytest.fixture()
def categories():
    expense_food = Category("餐饮-测试", CategoryType.EXPENSE, icon="🍔")
    income_salary = Category("工资-测试", CategoryType.INCOME, icon="💰")
    return expense_food, income_salary

@pytest.fixture()
def tags():
    t1 = Tag("work", color="#ff0000")
    t2 = Tag("fun", color="#00ff00")
    return t1, t2

def make_entry(user_id, category, title, amount, ts, note="", currency="CNY", tags=None):
    e = Entry(
        user_id=user_id,
        category=category,
        title=title,
        amount=Decimal(str(amount)),
        currency=currency,
        note=note,
        timestamp=ts,
    )
    if tags:
        for t in tags:
            e.add_tag(t)
    return e
