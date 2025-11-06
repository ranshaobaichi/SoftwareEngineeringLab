"""
PocketLedger 主程序
提供命令行交互界面
"""
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from pocket_ledger.app_logic import AppLogic
from pocket_ledger.ui_interface import ConsoleUI
from pocket_ledger.models.category import CategoryType
from pocket_ledger.models.budget import BudgetPeriod


class PocketLedgerCLI:
    """
    命令行界面控制器
    """
    
    def __init__(self):
        """初始化CLI"""
        self.app = AppLogic()
        self.ui = ConsoleUI()
        self.running = True
    
    def run(self) -> None:
        """运行主循环"""
        print("\n" + "="*60)
        print(" "*15 + "PocketLedger 记账系统")
        print(" "*20 + "v1.0.0")
        print("="*60)
        
        # 登录或注册
        while self.running and not self.app.auth_service.is_logged_in():
            self._show_auth_menu()
        
        # 主菜单循环
        while self.running and self.app.auth_service.is_logged_in():
            self._show_main_menu()
        
        print("\n感谢使用 PocketLedger!")
    
    def _show_auth_menu(self) -> None:
        """显示认证菜单"""
        print("\n请选择操作:")
        print("1. 登录")
        print("2. 注册")
        print("0. 退出")
        
        choice = input("\n请输入选项: ").strip()
        
        if choice == "1":
            self._handle_login()
        elif choice == "2":
            self._handle_register()
        elif choice == "0":
            self.running = False
        else:
            print("无效选项,请重试")
    
    def _handle_login(self) -> None:
        """处理登录"""
        self.ui.show_login_screen()
        
        email = input("邮箱: ").strip()
        password = input("密码: ").strip()
        
        success, message, user = self.app.login(email, password)
        
        if success:
            self.ui.show_message("登录成功", f"欢迎回来, {user.nickname}!", "success")
        else:
            self.ui.show_message("登录失败", message, "error")
    
    def _handle_register(self) -> None:
        """处理注册"""
        self.ui.show_register_screen()
        
        email = input("邮箱: ").strip()
        phone = input("手机号: ").strip()
        nickname = input("昵称: ").strip()
        password = input("密码: ").strip()
        password_confirm = input("确认密码: ").strip()
        
        if password != password_confirm:
            self.ui.show_message("注册失败", "两次密码不一致", "error")
            return
        
        success, message, user = self.app.register(email, phone, password, nickname)
        
        if success:
            self.ui.show_message("注册成功", "请登录", "success")
        else:
            self.ui.show_message("注册失败", message, "error")
    
    def _show_main_menu(self) -> None:
        """显示主菜单"""
        self.ui.show_main_screen()
        
        choice = input("\n请输入选项: ").strip()
        
        if choice == "1":
            self._handle_add_entry()
        elif choice == "2":
            self._handle_view_entries()
        elif choice == "3":
            self._handle_statistics()
        elif choice == "4":
            self._handle_budget()
        elif choice == "5":
            self._handle_export()
        elif choice == "6":
            self._handle_settings()
        elif choice == "0":
            self._handle_logout()
        else:
            print("无效选项,请重试")
    
    def _handle_add_entry(self) -> None:
        """处理添加账目"""
        self.ui.show_add_entry_dialog()
        
        # 选择类型
        print("\n选择类型:")
        print("1. 支出")
        print("2. 收入")
        type_choice = input("请选择: ").strip()
        
        if type_choice == "1":
            category_type = CategoryType.EXPENSE
        elif type_choice == "2":
            category_type = CategoryType.INCOME
        else:
            print("无效选择")
            return
        
        # 显示分类
        categories = self.app.get_categories_by_type(category_type)
        print(f"\n可用分类 ({category_type.value}):")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat.icon} {cat.name}")
        
        cat_choice = input("\n选择分类编号: ").strip()
        try:
            cat_index = int(cat_choice) - 1
            if 0 <= cat_index < len(categories):
                category = categories[cat_index]
            else:
                print("无效的分类编号")
                return
        except ValueError:
            print("请输入数字")
            return
        
        # 输入金额
        amount_str = input("金额: ").strip()
        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                print("金额必须大于0")
                return
        except:
            print("无效的金额格式")
            return
        
        # 输入标题
        title = input("标题: ").strip()
        if not title:
            print("标题不能为空")
            return
        
        # 输入备注(可选)
        note = input("备注(可选): ").strip()
        
        # 添加账目
        success, message, entry = self.app.add_entry(
            category_id=category.category_id,
            title=title,
            amount=amount,
            note=note if note else None
        )
        
        if success:
            self.ui.show_message("添加成功", f"已添加账目: {title}", "success")
        else:
            self.ui.show_message("添加失败", message, "error")
    
    def _handle_view_entries(self) -> None:
        """处理查看账目"""
        print("\n查询选项:")
        print("1. 查看全部")
        print("2. 按日期查询")
        print("3. 按关键词查询")
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        entries = []
        
        if choice == "1":
            entries = self.app.query_entries()
        elif choice == "2":
            days = input("查询最近几天的记录? ").strip()
            try:
                days_int = int(days)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_int)
                entries = self.app.query_entries(start_date=start_date, end_date=end_date)
            except:
                print("无效的天数")
                return
        elif choice == "3":
            keyword = input("输入关键词: ").strip()
            entries = self.app.query_entries(keyword=keyword)
        elif choice == "0":
            return
        else:
            print("无效选项")
            return
        
        self.ui.show_entry_list(entries)
        
        # 提供操作选项
        if entries:
            print("\n操作:")
            print("1. 删除账目")
            print("0. 返回")
            op = input("请选择: ").strip()
            
            if op == "1":
                try:
                    index = int(input("输入要删除的账目编号: ").strip()) - 1
                    if 0 <= index < len(entries):
                        entry = entries[index]
                        if self.ui.confirm_dialog("确认删除", f"确定要删除账目 '{entry.title}' 吗?"):
                            success, message = self.app.delete_entry(entry.entry_id)
                            self.ui.show_message("删除结果", message, "success" if success else "error")
                except:
                    print("无效的编号")
    
    def _handle_statistics(self) -> None:
        """处理统计"""
        print("\n统计选项:")
        print("1. 本月统计")
        print("2. 本年统计")
        print("3. 自定义时间范围")
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            # 本月统计
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1)
            end_date = now
            stats = self.app.get_summary_statistics(start_date, end_date)
            self.ui.show_statistics_screen(stats)
            
            # 分类统计
            print("\n分类统计:")
            cat_stats = self.app.get_category_statistics(start_date, end_date)
            for cat_name, data in cat_stats.items():
                print(f"{cat_name}: ¥{data['amount']:.2f} ({data['count']}笔, {data['percentage']:.1f}%)")
        
        elif choice == "2":
            # 本年统计
            now = datetime.now()
            monthly_stats = self.app.get_monthly_statistics(now.year)
            
            print(f"\n{now.year}年月度统计:")
            print("-" * 60)
            print(f"{'月份':<8} {'收入':>12} {'支出':>12} {'余额':>12}")
            print("-" * 60)
            
            for month_data in monthly_stats:
                month = month_data['month']
                income = month_data['income']
                expense = month_data['expense']
                balance = month_data['balance']
                print(f"{month:>2}月    ¥{income:>10.2f} ¥{expense:>10.2f} ¥{balance:>10.2f}")
            
            print("-" * 60)
        
        elif choice == "0":
            return
    
    def _handle_budget(self) -> None:
        """处理预算管理"""
        print("\n预算管理:")
        print("1. 查看预算状态")
        print("2. 添加新预算")
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            budgets = self.app.get_budget_status()
            self.ui.show_budget_screen(budgets)
        
        elif choice == "2":
            print("\n选择预算周期:")
            print("1. 每日")
            print("2. 每周")
            print("3. 每月")
            print("4. 每年")
            
            period_choice = input("请选择: ").strip()
            period_map = {
                "1": BudgetPeriod.DAILY,
                "2": BudgetPeriod.WEEKLY,
                "3": BudgetPeriod.MONTHLY,
                "4": BudgetPeriod.YEARLY
            }
            
            period = period_map.get(period_choice)
            if not period:
                print("无效选择")
                return
            
            amount_str = input("预算限额: ").strip()
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    print("金额必须大于0")
                    return
            except:
                print("无效的金额格式")
                return
            
            threshold = input("提醒阈值(百分比, 默认80): ").strip()
            if threshold:
                try:
                    threshold_int = int(threshold)
                except:
                    threshold_int = 80
            else:
                threshold_int = 80
            
            success, message, budget = self.app.add_budget(
                period=period,
                limit_amount=amount,
                threshold_percent=threshold_int
            )
            
            self.ui.show_message("添加结果", message, "success" if success else "error")
    
    def _handle_export(self) -> None:
        """处理导出"""
        print("\n导出数据:")
        print("1. 导出为Excel (.xlsx)")
        print("2. 导出为CSV (.csv)")
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        if choice in ["1", "2"]:
            file_path = input("输入文件路径(含文件名): ").strip()
            if not file_path:
                print("路径不能为空")
                return
            
            if choice == "1":
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                success, message = self.app.export_to_excel(file_path)
            else:
                if not file_path.endswith('.csv'):
                    file_path += '.csv'
                success, message = self.app.export_to_csv(file_path)
            
            self.ui.show_message("导出结果", message, "success" if success else "error")
    
    def _handle_settings(self) -> None:
        """处理个人设置"""
        user = self.app.get_current_user()
        
        print("\n个人设置:")
        print(f"昵称: {user.nickname}")
        print(f"邮箱: {user.email}")
        print(f"手机: {user.phone}")
        print("\n1. 修改昵称")
        print("2. 修改密码")
        print("3. 注销账户")
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            new_nickname = input("新昵称: ").strip()
            if new_nickname:
                success, message = self.app.update_profile(nickname=new_nickname)
                self.ui.show_message("更新结果", message, "success" if success else "error")
        
        elif choice == "2":
            old_password = input("旧密码: ").strip()
            new_password = input("新密码: ").strip()
            confirm_password = input("确认新密码: ").strip()
            
            if new_password != confirm_password:
                print("两次密码不一致")
                return
            
            success, message = self.app.change_password(old_password, new_password)
            self.ui.show_message("更新结果", message, "success" if success else "error")
        
        elif choice == "3":
            if self.ui.confirm_dialog("注销账户", "确定要注销账户吗?"):
                success, message = self.app.delete_current_user()
                if success:
                    self.ui.show_message("账户已注销", message, "success")
                else:
                    self.ui.show_message("注销失败", message, "error")

        self.run()
    
    def _handle_logout(self) -> None:
        """处理登出"""
        if self.ui.confirm_dialog("退出登录", "确定要退出吗?"):
            success, message = self.app.logout()
            self.ui.show_message("退出", message, "success")


def main():
    """主函数"""
    try:
        cli = PocketLedgerCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
