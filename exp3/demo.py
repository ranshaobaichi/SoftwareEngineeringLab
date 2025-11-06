"""
PocketLedger 功能演示和测试
"""
from datetime import datetime, timedelta
from decimal import Decimal

from pocket_ledger import AppLogic
from pocket_ledger.models.category import CategoryType
from pocket_ledger.models.budget import BudgetPeriod


def demo_basic_features():
    """演示基本功能"""
    print("\n" + "="*60)
    print("PocketLedger 功能演示")
    print("="*60)
    
    # 创建应用实例
    app = AppLogic(db_path="demo_ledger.json")
    
    # 1. 用户注册
    print("\n【1. 用户注册】")
    success, msg, user = app.register(
        email="demo@example.com",
        phone="13800138000",
        password="demo123",
        nickname="演示用户"
    )
    print(f"注册结果: {msg}")
    
    # 2. 用户登录
    print("\n【2. 用户登录】")
    success, msg, user = app.login("demo@example.com", "demo123")
    print(f"登录结果: {msg}")
    if success:
        print(f"当前用户: {user.nickname} ({user.email})")
    
    # 3. 获取分类
    print("\n【3. 查看可用分类】")
    expense_categories = app.get_categories_by_type(CategoryType.EXPENSE)
    income_categories = app.get_categories_by_type(CategoryType.INCOME)
    
    print(f"支出分类 ({len(expense_categories)}个):")
    for cat in expense_categories[:5]:
        print(f"  - {cat.icon} {cat.name}")
    
    print(f"\n收入分类 ({len(income_categories)}个):")
    for cat in income_categories[:3]:
        print(f"  - {cat.icon} {cat.name}")
    
    # 4. 添加账目
    print("\n【4. 添加账目】")
    
    # 添加几条支出记录
    expenses_data = [
        ("早餐", Decimal("15.5"), "包子+豆浆"),
        ("午餐", Decimal("35.0"), "公司食堂"),
        ("晚餐", Decimal("42.8"), "和朋友聚餐"),
        ("交通", Decimal("12.0"), "地铁卡充值"),
        ("购物", Decimal("199.0"), "买了一件衣服"),
    ]
    
    food_category = next(c for c in expense_categories if c.name == "餐饮")
    transport_category = next(c for c in expense_categories if c.name == "交通")
    shopping_category = next(c for c in expense_categories if c.name == "购物")
    
    success, msg, _ = app.add_entry(
        category_id=food_category.category_id,
        title="早餐",
        amount=Decimal("15.5"),
        note="包子+豆浆"
    )
    print(f"添加账目: 早餐 - {msg}")
    
    success, msg, _ = app.add_entry(
        category_id=food_category.category_id,
        title="午餐",
        amount=Decimal("35.0"),
        note="公司食堂"
    )
    print(f"添加账目: 午餐 - {msg}")
    
    success, msg, _ = app.add_entry(
        category_id=food_category.category_id,
        title="晚餐",
        amount=Decimal("42.8"),
        note="和朋友聚餐"
    )
    print(f"添加账目: 晚餐 - {msg}")
    
    success, msg, _ = app.add_entry(
        category_id=transport_category.category_id,
        title="交通费",
        amount=Decimal("12.0"),
        note="地铁卡充值"
    )
    print(f"添加账目: 交通费 - {msg}")
    
    success, msg, _ = app.add_entry(
        category_id=shopping_category.category_id,
        title="购物",
        amount=Decimal("199.0"),
        note="买了一件衣服"
    )
    print(f"添加账目: 购物 - {msg}")
    
    # 添加收入记录
    salary_category = next(c for c in income_categories if c.name == "工资")
    success, msg, _ = app.add_entry(
        category_id=salary_category.category_id,
        title="本月工资",
        amount=Decimal("8000.0"),
        note="公司发薪"
    )
    print(f"添加账目: 工资 - {msg}")
    
    # 5. 查询账目
    print("\n【5. 查询账目】")
    entries = app.query_entries()
    print(f"共有 {len(entries)} 条记录:")
    for i, entry in enumerate(entries[:5], 1):
        print(f"{i}. [{entry.category.type.value}] {entry.title} - "
              f"¥{entry.amount} ({entry.category.name})")
    
    # 6. 统计分析
    print("\n【6. 统计分析】")
    stats = app.get_summary_statistics()
    print(f"总收入: ¥{stats['total_income']:.2f}")
    print(f"总支出: ¥{stats['total_expense']:.2f}")
    print(f"余额:   ¥{stats['balance']:.2f}")
    
    # 分类统计
    print("\n分类统计:")
    cat_stats = app.get_category_statistics()
    for cat_name, data in list(cat_stats.items())[:5]:
        print(f"  {cat_name}: ¥{data['amount']:.2f} "
              f"({data['count']}笔, {data['percentage']:.1f}%)")
    
    # 7. 预算管理
    print("\n【7. 预算管理】")
    success, msg, budget = app.add_budget(
        period=BudgetPeriod.MONTHLY,
        limit_amount=Decimal("3000.0"),
        threshold_percent=80
    )
    print(f"设置月度预算: {msg}")
    
    budget_status = app.get_budget_status()
    if budget_status:
        for b in budget_status:
            print(f"\n预算周期: {b['period']}")
            print(f"预算限额: ¥{b['limit_amount']:.2f}")
            print(f"已用金额: ¥{b['current_amount']:.2f} ({b['percentage']:.1f}%)")
            print(f"剩余金额: ¥{b['remaining']:.2f}")
            if b['is_exceeded']:
                print("⚠️ 已超出预算!")
            elif b['is_threshold_reached']:
                print("⚠️ 已达到提醒阈值!")
    
    # 8. 数据导出
    print("\n【8. 数据导出】")
    success, msg = app.export_to_csv("demo_export.csv")
    print(f"导出CSV: {msg}")
    
    # 可选: 如果安装了openpyxl
    try:
        success, msg = app.export_to_excel("demo_export.xlsx")
        print(f"导出Excel: {msg}")
    except:
        print("导出Excel: 需要安装openpyxl库")
    
    print("\n" + "="*60)
    print("演示完成!")
    print("="*60)


def demo_advanced_features():
    """演示高级功能"""
    print("\n" + "="*60)
    print("高级功能演示")
    print("="*60)
    
    app = AppLogic(db_path="demo_ledger.json")
    
    # 登录
    app.login("demo@example.com", "demo123")
    
    # 1. 标签管理
    print("\n【1. 标签管理】")
    success, msg, tag1 = app.add_tag("必需", "#FF0000")
    success, msg, tag2 = app.add_tag("可选", "#00FF00")
    print(f"添加标签: {msg}")
    
    tags = app.get_all_tags()
    print(f"已有标签: {', '.join(t.name for t in tags)}")
    
    # 2. 复杂查询
    print("\n【2. 复杂查询】")
    
    # 按关键词搜索
    keyword_entries = app.query_entries(keyword="餐")
    print(f"关键词'餐'搜索结果: {len(keyword_entries)}条")
    
    # 按时间范围查询
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    recent_entries = app.query_entries(start_date=start_date, end_date=end_date)
    print(f"最近7天记录: {len(recent_entries)}条")
    
    # 3. 月度统计
    print("\n【3. 月度统计】")
    year = datetime.now().year
    monthly_stats = app.get_monthly_statistics(year)
    
    print(f"\n{year}年月度统计:")
    print("-" * 50)
    print(f"{'月份':<6} {'收入':>10} {'支出':>10} {'余额':>10}")
    print("-" * 50)
    
    current_month = datetime.now().month
    for month_data in monthly_stats[:current_month]:
        month = month_data['month']
        income = month_data['income']
        expense = month_data['expense']
        balance = month_data['balance']
        if income > 0 or expense > 0:
            print(f"{month:>2}月   ¥{income:>8.2f} ¥{expense:>8.2f} ¥{balance:>8.2f}")
    
    print("-" * 50)
    
    # 4. 个人信息管理
    print("\n【4. 个人信息管理】")
    success, msg = app.update_profile(nickname="新昵称")
    print(f"更新昵称: {msg}")
    
    user = app.get_current_user()
    print(f"当前用户信息: {user.nickname} ({user.email})")
    
    print("\n" + "="*60)
    print("高级功能演示完成!")
    print("="*60)


def run_all_demos():
    """运行所有演示"""
    print("\n" + "="*60)
    print("开始运行PocketLedger完整功能演示")
    print("="*60)
    
    # 基本功能演示
    demo_basic_features()
    
    # 高级功能演示
    demo_advanced_features()
    
    print("\n" + "="*60)
    print("所有演示完成!")
    print("="*60)
    print("\n提示:")
    print("- 演示数据已保存到 demo_ledger.json")
    print("- 导出文件: demo_export.csv 和 demo_export.xlsx")
    print("- 可以运行 'python main.py' 启动完整的CLI程序")
    print("="*60)


if __name__ == "__main__":
    run_all_demos()
