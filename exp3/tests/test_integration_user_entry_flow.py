from decimal import Decimal
from pocket_ledger.app_logic import AppLogic
from pocket_ledger.models.category import CategoryType


def test_integration_user_add_and_query_entry(tmp_path):
    """
    集成测试用例1：
    用户注册 -> 登录 -> 添加账目 -> 查询账目
    """

    # 1. 初始化 AppLogic（使用临时数据库）
    db_path = tmp_path / "integration_user_entry.json"
    app = AppLogic(str(db_path))

    # 2. 用户注册
    ok, msg, user = app.register(
        email="integration@test.com",
        phone="12345678",
        password="123456",
        nickname="integration_user"
    )
    assert ok, msg
    assert user is not None

    # 3. 用户登录
    ok, msg, user = app.login("integration@test.com", "123456")
    assert ok, msg

    # 4. 获取一个支出分类（数据库初始化时已创建默认分类）
    categories = app.get_categories_by_type(CategoryType.EXPENSE)
    assert categories
    category = categories[0]

    # 5. 添加账目
    ok, msg, entry = app.add_entry(
        category_id=category.category_id,
        title="integration lunch",
        amount=Decimal("25.50"),
        note="integration test"
    )
    assert ok, msg
    assert entry is not None

    # 6. 查询账目
    entries = app.query_entries()
    assert len(entries) == 1
    assert entries[0].title == "integration lunch"
    assert entries[0].amount == Decimal("25.50")
