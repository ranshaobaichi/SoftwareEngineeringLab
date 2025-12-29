import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
import tempfile

from hypothesis import given, settings, strategies as st

from pocket_ledger.database.database import Database
from pocket_ledger.models.category import Category, CategoryType
from pocket_ledger.models.entry import Entry


# --------- 辅助策略 ---------

def decimal_strategy():
    return st.decimals(
        min_value=-100000,
        max_value=100000,
        allow_nan=False,
        allow_infinity=False
    )

datetime_strategy = st.datetimes(
    min_value=datetime(2000, 1, 1),
    max_value=datetime(2030, 12, 31)
)

keyword_strategy = st.one_of(
    st.none(),
    st.text(min_size=0, max_size=200),
)


# --------- Hypothesis 模糊测试 ---------

@given(
    start_date=st.one_of(st.none(), datetime_strategy),
    end_date=st.one_of(st.none(), datetime_strategy),
    min_amount=st.one_of(st.none(), decimal_strategy()),
    max_amount=st.one_of(st.none(), decimal_strategy()),
    keyword=keyword_strategy,
)
@settings(max_examples=500)   # 你可以写 500 / 1000
def test_fuzz_query_entries(
    start_date,
    end_date,
    min_amount,
    max_amount,
    keyword
):
    """
    使用 Hypothesis 对 Database.query_entries 进行模糊测试，
    检查在随机及边界输入下是否发生崩溃。
    """

    # 构造基础数据
    user_id = uuid.uuid4()
    category = Category("fuzz", CategoryType.EXPENSE)

    # 每个 Hypothesis 样本单独创建一个全新的 DB 文件，避免状态串扰
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "test_db.json"
        db = Database(str(db_path))

        db.save_category(category)

        # 插入一些正常账目
        for i in range(5):
            e = Entry(
                user_id=user_id,
                category=category,
                title=f"entry{i}",
                amount=Decimal("10"),
                timestamp=datetime.now() - timedelta(days=i)
            )
            db.save_entry(e)

        # 核心：随机调用 query_entries
        try:
            db.query_entries(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                min_amount=min_amount,
                max_amount=max_amount,
                keyword=keyword
            )
        except Exception as e:
            # Hypothesis 一旦发现异常，会自动保存失败样例
            assert False, f"Crash detected: {e}"
