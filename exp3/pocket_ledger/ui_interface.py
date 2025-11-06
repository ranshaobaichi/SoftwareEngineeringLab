"""
UI接口层 - 为图形界面预留接口
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from .models.user import User
from .models.entry import Entry
from .models.category import Category, CategoryType
from .models.tag import Tag
from .models.budget import Budget, BudgetPeriod


class IUserInterface(ABC):
    """
    用户界面接口 - 定义UI需要实现的方法
    这个接口可以被GUI或CLI实现
    """
    
    @abstractmethod
    def show_login_screen(self) -> None:
        """显示登录界面"""
        pass
    
    @abstractmethod
    def show_register_screen(self) -> None:
        """显示注册界面"""
        pass
    
    @abstractmethod
    def show_main_screen(self) -> None:
        """显示主界面"""
        pass
    
    @abstractmethod
    def show_add_entry_dialog(self) -> None:
        """显示添加账目对话框"""
        pass
    
    @abstractmethod
    def show_entry_list(self, entries: List[Entry]) -> None:
        """
        显示账目列表
        
        Args:
            entries: 账目列表
        """
        pass
    
    @abstractmethod
    def show_statistics_screen(self, stats: Dict[str, Any]) -> None:
        """
        显示统计界面
        
        Args:
            stats: 统计数据
        """
        pass
    
    @abstractmethod
    def show_budget_screen(self, budgets: List[Dict[str, Any]]) -> None:
        """
        显示预算界面
        
        Args:
            budgets: 预算列表
        """
        pass
    
    @abstractmethod
    def show_message(self, title: str, message: str, msg_type: str = "info") -> None:
        """
        显示消息提示
        
        Args:
            title: 标题
            message: 消息内容
            msg_type: 消息类型(info/warning/error/success)
        """
        pass
    
    @abstractmethod
    def confirm_dialog(self, title: str, message: str) -> bool:
        """
        显示确认对话框
        
        Args:
            title: 标题
            message: 消息内容
            
        Returns:
            用户是否确认
        """
        pass
    
    @abstractmethod
    def get_file_path(self, title: str, file_types: str) -> Optional[str]:
        """
        获取文件路径(用于导出等操作)
        
        Args:
            title: 对话框标题
            file_types: 文件类型过滤
            
        Returns:
            选择的文件路径或None
        """
        pass


class ConsoleUI(IUserInterface):
    """
    控制台UI实现 - 简单的命令行界面实现
    用于演示和测试
    """
    
    def show_login_screen(self) -> None:
        """显示登录界面"""
        print("\n" + "="*50)
        print("欢迎使用 PocketLedger 记账系统")
        print("="*50)
        print("请登录您的账户")
    
    def show_register_screen(self) -> None:
        """显示注册界面"""
        print("\n" + "="*50)
        print("用户注册")
        print("="*50)
    
    def show_main_screen(self) -> None:
        """显示主界面"""
        print("\n" + "="*50)
        print("主菜单")
        print("="*50)
        print("1. 添加账目")
        print("2. 查看账目")
        print("3. 查看统计")
        print("4. 预算管理")
        print("5. 导出数据")
        print("6. 个人设置")
        print("0. 退出")
        print("="*50)
    
    def show_add_entry_dialog(self) -> None:
        """显示添加账目对话框"""
        print("\n" + "="*50)
        print("添加账目")
        print("="*50)
    
    def show_entry_list(self, entries: List[Entry]) -> None:
        """显示账目列表"""
        print("\n" + "="*50)
        print(f"账目列表 (共 {len(entries)} 条)")
        print("="*50)
        
        if not entries:
            print("暂无账目记录")
            return
        
        for i, entry in enumerate(entries, 1):
            print(f"\n{i}. [{entry.category.type.value}] {entry.title}")
            print(f"   金额: {entry.amount} {entry.currency}")
            print(f"   分类: {entry.category.name}")
            print(f"   时间: {entry.timestamp.strftime('%Y-%m-%d %H:%M')}")
            if entry.note:
                print(f"   备注: {entry.note}")
            if entry.tags:
                tags_str = ", ".join(tag.name for tag in entry.tags)
                print(f"   标签: {tags_str}")
        print("="*50)
    
    def show_statistics_screen(self, stats: Dict[str, Any]) -> None:
        """显示统计界面"""
        print("\n" + "="*50)
        print("统计分析")
        print("="*50)
        
        if 'total_income' in stats:
            print(f"总收入: ¥{stats['total_income']:.2f}")
            print(f"总支出: ¥{stats['total_expense']:.2f}")
            print(f"余额:   ¥{stats['balance']:.2f}")
        
        print("="*50)
    
    def show_budget_screen(self, budgets: List[Dict[str, Any]]) -> None:
        """显示预算界面"""
        print("\n" + "="*50)
        print(f"预算管理 (共 {len(budgets)} 项)")
        print("="*50)
        
        if not budgets:
            print("暂无预算设置")
            return
        
        for i, budget in enumerate(budgets, 1):
            print(f"\n{i}. 周期: {budget['period']}")
            print(f"   限额: ¥{budget['limit_amount']:.2f}")
            print(f"   已用: ¥{budget['current_amount']:.2f} ({budget['percentage']:.1f}%)")
            print(f"   剩余: ¥{budget['remaining']:.2f}")
            
            if budget['is_exceeded']:
                print("   ⚠️ 已超出预算!")
            elif budget['is_threshold_reached']:
                print("   ⚠️ 已达到提醒阈值!")
        
        print("="*50)
    
    def show_message(self, title: str, message: str, msg_type: str = "info") -> None:
        """显示消息提示"""
        symbols = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅'
        }
        symbol = symbols.get(msg_type, 'ℹ️')
        print(f"\n{symbol} {title}: {message}")
    
    def confirm_dialog(self, title: str, message: str) -> bool:
        """显示确认对话框"""
        print(f"\n{title}")
        print(message)
        response = input("确认? (y/n): ").strip().lower()
        return response in ['y', 'yes', '是']
    
    def get_file_path(self, title: str, file_types: str) -> Optional[str]:
        """获取文件路径"""
        print(f"\n{title}")
        print(f"文件类型: {file_types}")
        file_path = input("请输入文件路径: ").strip()
        return file_path if file_path else None


# 预留的GUI接口示例
class GUIInterface(IUserInterface):
    """
    图形界面接口 - 等待实现
    可以使用PyQt5、Tkinter等GUI框架实现
    """
    
    def __init__(self):
        """初始化GUI界面"""
        # TODO: 初始化GUI组件
        pass
    
    def show_login_screen(self) -> None:
        """显示登录界面"""
        # TODO: 实现GUI登录界面
        raise NotImplementedError("GUI界面待实现")
    
    def show_register_screen(self) -> None:
        """显示注册界面"""
        # TODO: 实现GUI注册界面
        raise NotImplementedError("GUI界面待实现")
    
    def show_main_screen(self) -> None:
        """显示主界面"""
        # TODO: 实现GUI主界面
        raise NotImplementedError("GUI界面待实现")
    
    def show_add_entry_dialog(self) -> None:
        """显示添加账目对话框"""
        # TODO: 实现添加账目对话框
        raise NotImplementedError("GUI界面待实现")
    
    def show_entry_list(self, entries: List[Entry]) -> None:
        """显示账目列表"""
        # TODO: 实现账目列表视图
        raise NotImplementedError("GUI界面待实现")
    
    def show_statistics_screen(self, stats: Dict[str, Any]) -> None:
        """显示统计界面"""
        # TODO: 实现统计图表界面
        raise NotImplementedError("GUI界面待实现")
    
    def show_budget_screen(self, budgets: List[Dict[str, Any]]) -> None:
        """显示预算界面"""
        # TODO: 实现预算管理界面
        raise NotImplementedError("GUI界面待实现")
    
    def show_message(self, title: str, message: str, msg_type: str = "info") -> None:
        """显示消息提示"""
        # TODO: 实现消息提示框
        raise NotImplementedError("GUI界面待实现")
    
    def confirm_dialog(self, title: str, message: str) -> bool:
        """显示确认对话框"""
        # TODO: 实现确认对话框
        raise NotImplementedError("GUI界面待实现")
    
    def get_file_path(self, title: str, file_types: str) -> Optional[str]:
        """获取文件路径"""
        # TODO: 实现文件选择对话框
        raise NotImplementedError("GUI界面待实现")
