from decimal import Decimal
from pocket_ledger.app_logic import AppLogic
from pocket_ledger.models.category import CategoryType
from pocket_ledger.models.budget import BudgetPeriod


def test_integration_budget_and_statistics(tmp_path):
    """
    集成测试用例2：
    添加账目 -> 添加预算 -> 统计与预算状态计算
    """

    # 1. 初始化 AppLogic
    db_path = tmp_path / "integration_budget_stat.json"
    app = AppLogic(str(db_path))

    # 2. 注册并登录用户
    app.register(
        email="stat@test.com",
        phone="12345678",
        password="abcdef",
        nickname="stat_user"
    )
    app.login("stat@test.com", "abcdef")

    # 3. 获取支出分类
    category = app.get_categories_by_type(CategoryType.EXPENSE)[0]

    # 4. 添加账目
    app.add_entry(category.category_id, "expense A", Decimal("100"))
    app.add_entry(category.category_id, "expense B", Decimal("50"))

    # 5. 添加预算
    ok, msg, budget = app.add_budget(
        period=BudgetPeriod.MONTHLY,
        limit_amount=Decimal("200"),
        threshold_percent=50
    )
    assert ok, msg
    assert budget is not None

    # 6. 查询预算状态
    status_list = app.get_budget_status()
    assert len(status_list) == 1

    status = status_list[0]
    assert status["current_amount"] == 150.0
    assert status["is_threshold_reached"] is True
    assert status["is_exceeded"] is False
