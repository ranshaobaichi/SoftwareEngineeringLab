# tests/test_database_query_entries.py
from datetime import datetime
from decimal import Decimal

from .conftest import make_entry

def test_query_entries_user_filter(db, user_ids, categories):
    u1, u2 = user_ids
    c_exp, _ = categories
    db.save_category(c_exp)

    e1 = make_entry(u1, c_exp, "lunch", "12.5", datetime(2025, 1, 1, 10, 0, 0))
    e2 = make_entry(u2, c_exp, "dinner", "20", datetime(2025, 1, 2, 10, 0, 0))
    db.save_entry(e1)
    db.save_entry(e2)

    res = db.query_entries(user_id=u1)
    assert len(res) == 1
    assert res[0].user_id == u1

def test_query_entries_category_filter(db, user_ids, categories):
    u1, _ = user_ids
    c_exp, c_inc = categories
    db.save_category(c_exp)
    db.save_category(c_inc)

    e1 = make_entry(u1, c_exp, "lunch", "12.5", datetime(2025, 1, 1, 10, 0, 0))
    e2 = make_entry(u1, c_inc, "salary", "1000", datetime(2025, 1, 2, 10, 0, 0))
    db.save_entry(e1)
    db.save_entry(e2)

    res = db.query_entries(user_id=u1, category_id=c_exp.category_id)
    assert len(res) == 1
    assert res[0].category.category_id == c_exp.category_id

def test_query_entries_tag_filter(db, user_ids, categories, tags):
    u1, _ = user_ids
    c_exp, _ = categories
    t1, t2 = tags
    db.save_category(c_exp)
    db.save_tag(t1)
    db.save_tag(t2)

    e1 = make_entry(u1, c_exp, "movie", "30", datetime(2025, 1, 3, 10, 0, 0), tags=[t1])
    e2 = make_entry(u1, c_exp, "coffee", "15", datetime(2025, 1, 4, 10, 0, 0), tags=[t2])
    db.save_entry(e1)
    db.save_entry(e2)

    res = db.query_entries(user_id=u1, tag_ids=[t1.tag_id])
    assert len(res) == 1
    assert res[0].title == "movie"

def test_query_entries_date_range_inclusive(db, user_ids, categories):
    u1, _ = user_ids
    c_exp, _ = categories
    db.save_category(c_exp)

    e1 = make_entry(u1, c_exp, "a", "1", datetime(2025, 1, 1, 0, 0, 0))
    e2 = make_entry(u1, c_exp, "b", "1", datetime(2025, 1, 2, 0, 0, 0))
    e3 = make_entry(u1, c_exp, "c", "1", datetime(2025, 1, 3, 0, 0, 0))
    for e in (e1, e2, e3):
        db.save_entry(e)

    start = datetime(2025, 1, 2, 0, 0, 0)
    end = datetime(2025, 1, 3, 0, 0, 0)
    res = db.query_entries(user_id=u1, start_date=start, end_date=end)
    # 代码里是 entry_time < start 跳过，entry_time > end 跳过，所以边界包含
    assert [x.title for x in res] == ["c", "b"]

def test_query_entries_amount_range(db, user_ids, categories):
    u1, _ = user_ids
    c_exp, _ = categories
    db.save_category(c_exp)

    e1 = make_entry(u1, c_exp, "a", "10", datetime(2025, 1, 1, 10, 0, 0))
    e2 = make_entry(u1, c_exp, "b", "20", datetime(2025, 1, 1, 11, 0, 0))
    e3 = make_entry(u1, c_exp, "c", "30", datetime(2025, 1, 1, 12, 0, 0))
    for e in (e1, e2, e3):
        db.save_entry(e)

    res = db.query_entries(user_id=u1, min_amount=Decimal("15"), max_amount=Decimal("25"))
    assert [x.title for x in res] == ["b"]

def test_query_entries_keyword_title_case_insensitive(db, user_ids, categories):
    u1, _ = user_ids
    c_exp, _ = categories
    db.save_category(c_exp)

    db.save_entry(make_entry(u1, c_exp, "Buy Apple", "10", datetime(2025, 1, 1, 10, 0, 0)))
    db.save_entry(make_entry(u1, c_exp, "buy orange", "10", datetime(2025, 1, 1, 11, 0, 0)))

    res = db.query_entries(user_id=u1, keyword="APPLE")
    assert len(res) == 1
    assert res[0].title == "Buy Apple"

def test_query_entries_keyword_note(db, user_ids, categories):
    u1, _ = user_ids
    c_exp, _ = categories
    db.save_category(c_exp)

    db.save_entry(make_entry(u1, c_exp, "x", "10", datetime(2025, 1, 1, 10, 0, 0), note="for project"))
    db.save_entry(make_entry(u1, c_exp, "y", "10", datetime(2025, 1, 1, 11, 0, 0), note="for fun"))

    res = db.query_entries(user_id=u1, keyword="PROJECT")
    assert len(res) == 1
    assert res[0].title == "x"

def test_query_entries_sort_desc_by_timestamp(db, user_ids, categories):
    u1, _ = user_ids
    c_exp, _ = categories
    db.save_category(c_exp)

    db.save_entry(make_entry(u1, c_exp, "old", "10", datetime(2025, 1, 1, 10, 0, 0)))
    db.save_entry(make_entry(u1, c_exp, "new", "10", datetime(2025, 1, 2, 10, 0, 0)))
    res = db.query_entries(user_id=u1)
    assert [x.title for x in res] == ["new", "old"]

def test_query_entries_combined_filters(db, user_ids, categories, tags):
    u1, _ = user_ids
    c_exp, _ = categories
    t1, _t2 = tags
    db.save_category(c_exp)
    db.save_tag(t1)

    db.save_entry(make_entry(u1, c_exp, "match", "50", datetime(2025, 1, 2, 10, 0, 0), note="alpha", tags=[t1]))
    db.save_entry(make_entry(u1, c_exp, "nomatch", "5", datetime(2025, 1, 2, 9, 0, 0), note="alpha", tags=[t1]))

    res = db.query_entries(
        user_id=u1,
        tag_ids=[t1.tag_id],
        min_amount=Decimal("10"),
        keyword="alpha",
        start_date=datetime(2025, 1, 2, 0, 0, 0),
        end_date=datetime(2025, 1, 2, 23, 59, 59),
    )
    assert len(res) == 1
    assert res[0].title == "match"
