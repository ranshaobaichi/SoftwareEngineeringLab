"""
预算模型
"""
import uuid
from enum import Enum
from typing import Optional
from decimal import Decimal

class BudgetPeriod(Enum):
    """预算周期枚举"""
    DAILY = "daily"  # 每日
    WEEKLY = "weekly"  # 每周
    MONTHLY = "monthly"  # 每月
    YEARLY = "yearly"  # 每年


class Budget:
    """
    预算类 - 管理用户预算和提醒
    
    Attributes:
        budget_id: 预算唯一标识符
        user_id: 所属用户ID
        category_id: 关联分类ID(可选,None表示总预算)
        period: 预算周期
        limit_amount: 预算限额
        threshold_percent: 提醒阈值百分比(0-100)
        is_active: 是否启用
    """
    
    def __init__(
        self,
        user_id: uuid.UUID,
        period: BudgetPeriod,
        limit_amount: Decimal,
        threshold_percent: int = 80,
        category_id: Optional[uuid.UUID] = None,
        is_active: bool = True,
        budget_id: Optional[uuid.UUID] = None
    ):
        """
        初始化预算对象
        
        Args:
            user_id: 用户ID
            period: 预算周期
            limit_amount: 预算限额
            threshold_percent: 提醒阈值百分比(默认80%)
            category_id: 分类ID(可选)
            is_active: 是否启用(默认True)
            budget_id: 预算ID(可选,默认自动生成)
        """
        self.budget_id = budget_id if budget_id else uuid.uuid4()
        self.user_id = user_id
        self.category_id = category_id
        self.period = period
        self.limit_amount = Decimal(str(limit_amount))
        self.threshold_percent = self._validate_threshold(threshold_percent)
        self.is_active = is_active
    
    def _validate_threshold(self, threshold: int) -> int:
        """
        验证阈值百分比是否有效
        
        Args:
            threshold: 阈值百分比
            
        Returns:
            有效的阈值百分比
            
        Raises:
            ValueError: 阈值超出范围
        """
        if not 0 <= threshold <= 100:
            raise ValueError("阈值百分比必须在0-100之间")
        return threshold
    
    def is_exceeded(self, current_amount: Decimal) -> bool:
        """
        判断当前金额是否超过预算限额
        
        Args:
            current_amount: 当前支出金额
            
        Returns:
            是否超过预算
        """
        return Decimal(str(current_amount)) > self.limit_amount
    
    def is_threshold_reached(self, current_amount: Decimal) -> bool:
        """
        判断当前金额是否达到提醒阈值
        
        Args:
            current_amount: 当前支出金额
            
        Returns:
            是否达到阈值
        """
        threshold_amount = self.limit_amount * Decimal(self.threshold_percent) / Decimal(100)
        return Decimal(str(current_amount)) >= threshold_amount
    
    def get_remaining_amount(self, current_amount: Decimal) -> Decimal:
        """
        获取剩余预算金额
        
        Args:
            current_amount: 当前支出金额
            
        Returns:
            剩余金额(可能为负数)
        """
        return self.limit_amount - Decimal(str(current_amount))
    
    def get_usage_percentage(self, current_amount: Decimal) -> float:
        """
        获取预算使用百分比
        
        Args:
            current_amount: 当前支出金额
            
        Returns:
            使用百分比(0-100+)
        """
        if self.limit_amount == 0:
            return 0.0
        return float((Decimal(str(current_amount)) / self.limit_amount) * 100)
    
    def update_limit(self, new_limit: Decimal) -> None:
        """
        更新预算限额
        
        Args:
            new_limit: 新的预算限额
        """
        self.limit_amount = Decimal(str(new_limit))
    
    def update_threshold(self, new_threshold: int) -> None:
        """
        更新提醒阈值
        
        Args:
            new_threshold: 新的阈值百分比
        """
        self.threshold_percent = self._validate_threshold(new_threshold)
    
    def activate(self) -> None:
        """启用预算"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """停用预算"""
        self.is_active = False
    
    def to_dict(self) -> dict:
        """
        将预算对象转换为字典
        
        Returns:
            预算信息字典
        """
        return {
            'budget_id': str(self.budget_id),
            'user_id': str(self.user_id),
            'category_id': str(self.category_id) if self.category_id else None,
            'period': self.period.value,
            'limit_amount': str(self.limit_amount),
            'threshold_percent': self.threshold_percent,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Budget':
        """
        从字典创建预算对象
        
        Args:
            data: 预算信息字典
            
        Returns:
            Budget对象
        """
        return cls(
            user_id=uuid.UUID(data['user_id']),
            period=BudgetPeriod(data['period']),
            limit_amount=Decimal(data['limit_amount']),
            threshold_percent=data['threshold_percent'],
            category_id=uuid.UUID(data['category_id']) if data.get('category_id') else None,
            is_active=data.get('is_active', True),
            budget_id=uuid.UUID(data['budget_id'])
        )
    
    def __repr__(self) -> str:
        """返回预算对象的字符串表示"""
        category_info = f"category_id={self.category_id}" if self.category_id else "总预算"
        return (f"Budget(id={self.budget_id}, {category_info}, "
                f"period={self.period.value}, limit={self.limit_amount})")
    
    def __eq__(self, other) -> bool:
        """判断两个预算对象是否相等"""
        if not isinstance(other, Budget):
            return False
        return self.budget_id == other.budget_id
