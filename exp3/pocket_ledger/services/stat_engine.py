"""
统计引擎 - 处理数据统计和分析
"""
import uuid
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta, time
from decimal import Decimal
from collections import defaultdict

from ..models.entry import Entry
from ..models.category import Category, CategoryType
from ..database.database import Database


class StatEngine:
    """
    统计引擎类 - 提供数据统计和分析功能
    
    Attributes:
        database: 数据库实例
    """
    
    def __init__(self, database: Database):
        """
        初始化统计引擎
        
        Args:
            database: 数据库实例
        """
        self.database = database
    
    def calculate_total_by_type(
        self,
        user_id: uuid.UUID,
        category_type: CategoryType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """
        计算指定类型的总金额
        
        Args:
            user_id: 用户ID
            category_type: 分类类型(收入/支出)
            start_date: 起始日期(可选)
            end_date: 结束日期(可选)
            
        Returns:
            总金额
        """
        entries = self.database.query_entries(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        total = Decimal('0')
        for entry in entries:
            if entry.category.type == category_type:
                total += entry.amount
        
        return total
    
    def calculate_balance(
        self,
        user_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """
        计算收支平衡(收入-支出)
        
        Args:
            user_id: 用户ID
            start_date: 起始日期(可选)
            end_date: 结束日期(可选)
            
        Returns:
            平衡金额
        """
        income = self.calculate_total_by_type(
            user_id, CategoryType.INCOME, start_date, end_date
        )
        expense = self.calculate_total_by_type(
            user_id, CategoryType.EXPENSE, start_date, end_date
        )
        return income - expense
    
    def get_statistics_by_category(
        self,
        user_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Dict[str, any]]:
        """
        按分类统计
        
        Args:
            user_id: 用户ID
            start_date: 起始日期(可选)
            end_date: 结束日期(可选)
            
        Returns:
            分类统计字典 {分类名称: {总金额, 次数, 百分比}}
        """
        entries = self.database.query_entries(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # 按分类汇总
        category_stats = defaultdict(lambda: {'amount': Decimal('0'), 'count': 0})
        total_amount = Decimal('0')
        
        for entry in entries:
            category_name = entry.category.name
            category_stats[category_name]['amount'] += entry.amount
            category_stats[category_name]['count'] += 1
            total_amount += entry.amount
        
        # 计算百分比
        result = {}
        for category_name, stats in category_stats.items():
            percentage = (stats['amount'] / total_amount * 100) if total_amount > 0 else 0
            result[category_name] = {
                'amount': stats['amount'],
                'count': stats['count'],
                'percentage': float(percentage)
            }
        
        return result
    
    def get_statistics_by_tag(
        self,
        user_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Dict[str, any]]:
        """
        按标签统计
        
        Args:
            user_id: 用户ID
            start_date: 起始日期(可选)
            end_date: 结束日期(可选)
            
        Returns:
            标签统计字典 {标签名称: {总金额, 次数}}
        """
        entries = self.database.query_entries(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # 按标签汇总
        tag_stats = defaultdict(lambda: {'amount': Decimal('0'), 'count': 0})
        
        for entry in entries:
            for tag in entry.tags:
                tag_stats[tag.name]['amount'] += entry.amount
                tag_stats[tag.name]['count'] += 1
        
        return dict(tag_stats)
    
    def get_daily_statistics(
        self,
        user_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        获取每日统计

        注意：
        - 本方法按“日期”维度统计，因此会将查询范围归一化到整天：
          start_date 当天 00:00:00 到 end_date 当天 23:59:59.999999
        - 对于非 INCOME/EXPENSE 的分类类型，默认忽略（避免误计为支出）。
        """
        if start_date is None or end_date is None:
            raise ValueError("start_date 和 end_date 不能为空")
        if start_date > end_date:
            raise ValueError("start_date 不能晚于 end_date")

        # 归一化为整天范围，避免结束日因时间为 00:00:00 等导致漏数据
        start_dt = datetime.combine(start_date.date(), time.min, tzinfo=start_date.tzinfo)
        end_dt = datetime.combine(end_date.date(), time.max, tzinfo=end_date.tzinfo)

        entries = self.database.query_entries(
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt
        ) or []

        daily_stats = defaultdict(lambda: {
            'income': Decimal('0'),
            'expense': Decimal('0')
        })

        for entry in entries:
            # 防御式：避免异常数据导致崩溃
            if entry is None or entry.timestamp is None or entry.category is None:
                continue

            date_key = entry.timestamp.date()
            ctype = getattr(entry.category, "type", None)

            if ctype == CategoryType.INCOME:
                daily_stats[date_key]['income'] += entry.amount
            elif ctype == CategoryType.EXPENSE:
                daily_stats[date_key]['expense'] += entry.amount
            else:
                # 未知类型：忽略（也可以改为 raise 或记录日志）
                continue

        result: List[Dict[str, Any]] = []
        current_date = start_dt.date()
        end_date_only = end_dt.date()

        while current_date <= end_date_only:
            stats = daily_stats[current_date]
            income = stats['income']
            expense = stats['expense']
            result.append({
                'date': current_date.isoformat(),
                'income': float(income),
                'expense': float(expense),
                'balance': float(income - expense)
            })
            current_date += timedelta(days=1)

        return result
    
    def get_monthly_statistics(
        self,
        user_id: uuid.UUID,
        year: int
    ) -> List[Dict[str, any]]:
        """
        获取月度统计
        
        Args:
            user_id: 用户ID
            year: 年份
            
        Returns:
            月度统计列表 [{月份, 收入, 支出, 平衡}]
        """
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
        
        entries = self.database.query_entries(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # 按月份汇总
        monthly_stats = defaultdict(lambda: {
            'income': Decimal('0'),
            'expense': Decimal('0')
        })
        
        for entry in entries:
            month_key = entry.timestamp.month
            if entry.category.type == CategoryType.INCOME:
                monthly_stats[month_key]['income'] += entry.amount
            else:
                monthly_stats[month_key]['expense'] += entry.amount
        
        # 转换为列表
        result = []
        for month in range(1, 13):
            stats = monthly_stats[month]
            result.append({
                'month': month,
                'income': float(stats['income']),
                'expense': float(stats['expense']),
                'balance': float(stats['income'] - stats['expense'])
            })
        
        return result
    
    def get_top_expenses(
        self,
        user_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10
    ) -> List[Entry]:
        """
        获取最大的支出记录
        
        Args:
            user_id: 用户ID
            start_date: 起始日期(可选)
            end_date: 结束日期(可选)
            limit: 返回数量限制
            
        Returns:
            支出条目列表
        """
        entries = self.database.query_entries(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # 筛选支出并排序
        expenses = [e for e in entries if e.category.type == CategoryType.EXPENSE]
        expenses.sort(key=lambda e: e.amount, reverse=True)
        
        return expenses[:limit]
    
    def check_budget_status(
        self,
        user_id: uuid.UUID
    ) -> List[Dict[str, any]]:
        """
        检查预算状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            预算状态列表
        """
        budgets = self.database.get_budgets_by_user(user_id)
        result = []
        
        for budget in budgets:
            if not budget.is_active:
                continue
            
            # 计算时间范围
            start_date, end_date = self._get_period_range(budget.period)
            
            # 计算当前支出
            current_amount = self.calculate_total_by_type(
                user_id,
                CategoryType.EXPENSE,
                start_date,
                end_date
            )
            
            # 如果是分类预算,只计算该分类
            if budget.category_id:
                entries = self.database.query_entries(
                    user_id=user_id,
                    category_id=budget.category_id,
                    start_date=start_date,
                    end_date=end_date
                )
                current_amount = sum(e.amount for e in entries if e.category.type == CategoryType.EXPENSE)
            
            result.append({
                'budget_id': str(budget.budget_id),
                'period': budget.period.value,
                'limit_amount': float(budget.limit_amount),
                'current_amount': float(current_amount),
                'remaining': float(budget.get_remaining_amount(current_amount)),
                'percentage': budget.get_usage_percentage(current_amount),
                'is_exceeded': budget.is_exceeded(current_amount),
                'is_threshold_reached': budget.is_threshold_reached(current_amount)
            })
        
        return result
    
    @staticmethod
    def _get_period_range(period) -> Tuple[datetime, datetime]:
        """
        获取预算周期的时间范围
        
        Args:
            period: 预算周期
            
        Returns:
            (起始时间, 结束时间)
        """
        from ..models.budget import BudgetPeriod
        
        now = datetime.now()
        
        if period == BudgetPeriod.DAILY:
            start = datetime(now.year, now.month, now.day, 0, 0, 0)
            end = datetime(now.year, now.month, now.day, 23, 59, 59)
        elif period == BudgetPeriod.WEEKLY:
            # 本周一到周日
            weekday = now.weekday()
            start = now - timedelta(days=weekday)
            start = datetime(start.year, start.month, start.day, 0, 0, 0)
            end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif period == BudgetPeriod.MONTHLY:
            start = datetime(now.year, now.month, 1, 0, 0, 0)
            # 下个月的第一天减一天
            if now.month == 12:
                end = datetime(now.year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
            else:
                end = datetime(now.year, now.month + 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:  # YEARLY
            start = datetime(now.year, 1, 1, 0, 0, 0)
            end = datetime(now.year, 12, 31, 23, 59, 59)
        
        return start, end
