"""
应用逻辑层 - 整合各个服务
"""
import uuid
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from decimal import Decimal

from .models.user import User
from .models.entry import Entry
from .models.category import Category, CategoryType
from .models.tag import Tag
from .models.budget import Budget, BudgetPeriod
from .database.database import Database
from .services.auth_service import AuthService
from .services.stat_engine import StatEngine
from .services.export_service import ExportService


class AppLogic:
    """
    应用逻辑类 - 整合所有服务,提供统一的业务接口
    
    Attributes:
        database: 数据库实例
        auth_service: 认证服务
        stat_engine: 统计引擎
        export_service: 导出服务
    """
    
    def __init__(self, db_path: str = "pocket_ledger.json"):
        """
        初始化应用逻辑
        
        Args:
            db_path: 数据库文件路径
        """
        self.database = Database(db_path)
        self.auth_service = AuthService(self.database)
        self.stat_engine = StatEngine(self.database)
        self.export_service = ExportService(self.database)
    
    # ========== 用户认证相关 ==========
    
    def register(
        self,
        email: str,
        phone: str,
        password: str,
        nickname: str,
        avatar_path: Optional[str] = None
    ) -> Tuple[bool, str, Optional[User]]:
        """
        用户注册
        
        Returns:
            (是否成功, 消息, 用户对象)
        """
        return self.auth_service.register(email, phone, password, nickname, avatar_path)
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        用户登录
        
        Returns:
            (是否成功, 消息, 用户对象)
        """
        return self.auth_service.login(email, password)
    
    def logout(self) -> Tuple[bool, str]:
        """
        用户登出
        
        Returns:
            (是否成功, 消息)
        """
        return self.auth_service.logout()
    
    def get_current_user(self) -> Optional[User]:
        """获取当前登录用户"""
        return self.auth_service.get_current_user()
    
    def update_profile(
        self,
        nickname: Optional[str] = None,
        avatar_path: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        更新用户资料
        
        Returns:
            (是否成功, 消息)
        """
        return self.auth_service.update_profile(nickname, avatar_path, phone)
    
    def change_password(self, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        修改密码
        
        Returns:
            (是否成功, 消息)
        """
        return self.auth_service.change_password(old_password, new_password)
    
    def delete_current_user(self) -> Tuple[bool, str]:
        """
        注销当前用户
        
        Returns:
            (是否成功, 消息)
        """
        user = self.auth_service.get_current_user()
        if not user:
            return False, "未登录"
        
        # 删除用户相关数据
        if self.database.delete_user(user.user_id):
            # 登出用户
            self.auth_service.logout()
            return True, "账户已注销"
        else:
            return False, "注销失败"

    # ========== 账目管理相关 ==========
    
    def add_entry(
        self,
        category_id: uuid.UUID,
        title: str,
        amount: Decimal,
        currency: str = "CNY",
        note: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        tag_ids: Optional[List[uuid.UUID]] = None,
        images: Optional[List[str]] = None
    ) -> Tuple[bool, str, Optional[Entry]]:
        """
        添加账目
        
        Returns:
            (是否成功, 消息, 条目对象)
        """
        user = self.auth_service.get_current_user()
        if not user:
            return False, "未登录", None
        
        # 获取分类
        category = self.database.get_category_by_id(category_id)
        if not category:
            return False, "分类不存在", None
        
        # 创建条目
        entry = Entry(
            user_id=user.user_id,
            category=category,
            title=title,
            amount=amount,
            currency=currency,
            note=note,
            timestamp=timestamp,
            images=images
        )
        
        # 添加标签
        if tag_ids:
            for tag_id in tag_ids:
                tag = self.database.get_tag_by_id(tag_id)
                if tag:
                    entry.add_tag(tag)
        
        # 保存到数据库
        if self.database.save_entry(entry):
            return True, "添加成功", entry
        else:
            return False, "添加失败", None
    
    def update_entry(
        self,
        entry_id: uuid.UUID,
        title: Optional[str] = None,
        amount: Optional[Decimal] = None,
        category_id: Optional[uuid.UUID] = None,
        note: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        更新账目
        
        Returns:
            (是否成功, 消息)
        """
        entry = self.database.get_entry_by_id(entry_id)
        if not entry:
            return False, "账目不存在"
        
        # 验证权限
        user = self.auth_service.get_current_user()
        if not user or entry.user_id != user.user_id:
            return False, "无权限修改"
        
        # 更新字段
        if title:
            entry.title = title
        if amount:
            entry.update_amount(amount)
        if category_id:
            category = self.database.get_category_by_id(category_id)
            if category:
                entry.update_category(category)
        if note is not None:
            entry.update_note(note)
        
        # 保存
        if self.database.save_entry(entry):
            return True, "更新成功"
        else:
            return False, "更新失败"
    
    def delete_entry(self, entry_id: uuid.UUID) -> Tuple[bool, str]:
        """
        删除账目
        
        Returns:
            (是否成功, 消息)
        """
        entry = self.database.get_entry_by_id(entry_id)
        if not entry:
            return False, "账目不存在"
        
        # 验证权限
        user = self.auth_service.get_current_user()
        if not user or entry.user_id != user.user_id:
            return False, "无权限删除"
        
        if self.database.delete_entry(entry_id):
            return True, "删除成功"
        else:
            return False, "删除失败"
    
    def query_entries(
        self,
        category_id: Optional[uuid.UUID] = None,
        tag_ids: Optional[List[uuid.UUID]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        keyword: Optional[str] = None
    ) -> List[Entry]:
        """
        查询账目
        
        Returns:
            条目列表
        """
        user = self.auth_service.get_current_user()
        if not user:
            return []
        
        return self.database.query_entries(
            user_id=user.user_id,
            category_id=category_id,
            tag_ids=tag_ids,
            start_date=start_date,
            end_date=end_date,
            keyword=keyword
        )
    
    # ========== 分类管理相关 ==========
    
    def get_all_categories(self) -> List[Category]:
        """获取所有分类"""
        return self.database.get_all_categories()
    
    def get_categories_by_type(self, category_type: CategoryType) -> List[Category]:
        """获取指定类型的分类"""
        return self.database.get_categories_by_type(category_type)
    
    def add_category(
        self,
        name: str,
        category_type: CategoryType,
        icon: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Category]]:
        """
        添加分类
        
        Returns:
            (是否成功, 消息, 分类对象)
        """
        category = Category(name=name, category_type=category_type, icon=icon)
        if self.database.save_category(category):
            return True, "添加成功", category
        else:
            return False, "添加失败", None
    
    # ========== 标签管理相关 ==========
    
    def get_all_tags(self) -> List[Tag]:
        """获取所有标签"""
        return self.database.get_all_tags()
    
    def add_tag(
        self,
        name: str,
        color: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Tag]]:
        """
        添加标签
        
        Returns:
            (是否成功, 消息, 标签对象)
        """
        tag = Tag(name=name, color=color)
        if self.database.save_tag(tag):
            return True, "添加成功", tag
        else:
            return False, "添加失败", None
    
    def add_tag_to_entry(
        self,
        entry_id: uuid.UUID,
        tag_id: uuid.UUID
    ) -> Tuple[bool, str]:
        """
        给账目添加标签
        
        Returns:
            (是否成功, 消息)
        """
        entry = self.database.get_entry_by_id(entry_id)
        if not entry:
            return False, "账目不存在"
        
        tag = self.database.get_tag_by_id(tag_id)
        if not tag:
            return False, "标签不存在"
        
        if entry.add_tag(tag):
            self.database.save_entry(entry)
            return True, "添加标签成功"
        else:
            return False, "标签已存在"
    
    # ========== 预算管理相关 ==========
    
    def add_budget(
        self,
        period: BudgetPeriod,
        limit_amount: Decimal,
        threshold_percent: int = 80,
        category_id: Optional[uuid.UUID] = None
    ) -> Tuple[bool, str, Optional[Budget]]:
        """
        添加预算
        
        Returns:
            (是否成功, 消息, 预算对象)
        """
        user = self.auth_service.get_current_user()
        if not user:
            return False, "未登录", None
        
        budget = Budget(
            user_id=user.user_id,
            period=period,
            limit_amount=limit_amount,
            threshold_percent=threshold_percent,
            category_id=category_id
        )
        
        if self.database.save_budget(budget):
            return True, "添加成功", budget
        else:
            return False, "添加失败", None
    
    def get_budget_status(self) -> List[Dict[str, Any]]:
        """
        获取预算状态
        
        Returns:
            预算状态列表
        """
        user = self.auth_service.get_current_user()
        if not user:
            return []
        
        return self.stat_engine.check_budget_status(user.user_id)
    
    # ========== 统计分析相关 ==========
    
    def get_summary_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取汇总统计
        
        Returns:
            统计数据字典
        """
        user = self.auth_service.get_current_user()
        if not user:
            return {}
        
        total_income = self.stat_engine.calculate_total_by_type(
            user.user_id, CategoryType.INCOME, start_date, end_date
        )
        total_expense = self.stat_engine.calculate_total_by_type(
            user.user_id, CategoryType.EXPENSE, start_date, end_date
        )
        balance = total_income - total_expense
        
        return {
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'balance': float(balance)
        }
    
    def get_category_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        获取分类统计
        
        Returns:
            分类统计字典
        """
        user = self.auth_service.get_current_user()
        if not user:
            return {}
        
        return self.stat_engine.get_statistics_by_category(
            user.user_id, start_date, end_date
        )
    
    def get_monthly_statistics(self, year: int) -> List[Dict[str, Any]]:
        """
        获取月度统计
        
        Returns:
            月度统计列表
        """
        user = self.auth_service.get_current_user()
        if not user:
            return []
        
        return self.stat_engine.get_monthly_statistics(user.user_id, year)
    
    # ========== 导出相关 ==========
    
    def export_to_excel(
        self,
        file_path: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[bool, str]:
        """
        导出账目到Excel
        
        Returns:
            (是否成功, 消息)
        """
        user = self.auth_service.get_current_user()
        if not user:
            return False, "未登录"
        
        entries = self.database.query_entries(
            user_id=user.user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not entries:
            return False, "没有数据可导出"
        
        if self.export_service.export_to_xlsx(entries, file_path):
            return True, f"成功导出 {len(entries)} 条记录"
        else:
            return False, "导出失败"
    
    def export_to_csv(
        self,
        file_path: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[bool, str]:
        """
        导出账目到CSV
        
        Returns:
            (是否成功, 消息)
        """
        user = self.auth_service.get_current_user()
        if not user:
            return False, "未登录"
        
        entries = self.database.query_entries(
            user_id=user.user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not entries:
            return False, "没有数据可导出"
        
        if self.export_service.export_to_csv(entries, file_path):
            return True, f"成功导出 {len(entries)} 条记录"
        else:
            return False, "导出失败"
