"""
预算模型
"""
import uuid
from enum import Enum
from typing import Optional, Union
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
        self.budget_id = budget_id if budget_id else uuid.uuid4()

        # ---- 基本类型校验（避免“带病对象”）----
        if not isinstance(user_id, uuid.UUID):
            raise TypeError("user_id 必须是 uuid.UUID")
        if category_id is not None and not isinstance(category_id, uuid.UUID):
            raise TypeError("category_id 必须是 uuid.UUID 或 None")
        if not isinstance(period, BudgetPeriod):
            raise TypeError("period 必须是 BudgetPeriod")
        if not isinstance(is_active, bool):
            raise TypeError("is_active 必须是 bool")

        self.user_id = user_id
        self.category_id = category_id
        self.period = period

        # ---- 金额与阈值校验（数据完整性关键）----
        self.limit_amount = self._validate_limit_amount(limit_amount)
        self.threshold_percent = self._validate_threshold(threshold_percent)
        self.is_active = is_active

    def _to_decimal(self, value: Union[Decimal, int, float, str], name: str) -> Decimal:
        """统一将输入转换为 Decimal；失败时给出明确错误。"""
        try:
            return value if isinstance(value, Decimal) else Decimal(str(value))
        except Exception as e:
            raise TypeError(f"{name} 无法转换为 Decimal: {e}")

    def _validate_limit_amount(self, limit_amount: Union[Decimal, int, float, str]) -> Decimal:
        """
        验证预算限额是否有效：必须为正数（建议 > 0）。
        若你的业务允许 0 预算，把条件改成 >= 0 并同步调整相关逻辑/测试。
        """
        amt = self._to_decimal(limit_amount, "limit_amount")
        if amt <= 0:
            raise ValueError("limit_amount 必须大于 0")
        return amt

    def _validate_current_amount(self, current_amount: Union[Decimal, int, float, str]) -> Decimal:
        """验证当前支出金额：必须是非负数。"""
        amt = self._to_decimal(current_amount, "current_amount")
        if amt < 0:
            raise ValueError("current_amount 不能为负数")
        return amt

    def _validate_threshold(self, threshold: int) -> int:
        if not isinstance(threshold, int):
            raise TypeError("threshold_percent 必须是 int")
        if not 0 <= threshold <= 100:
            raise ValueError("阈值百分比必须在0-100之间")
        return threshold

    def is_exceeded(self, current_amount: Decimal) -> bool:
        amt = self._validate_current_amount(current_amount)
        return amt > self.limit_amount

    def is_threshold_reached(self, current_amount: Decimal) -> bool:
        amt = self._validate_current_amount(current_amount)
        threshold_amount = self.limit_amount * Decimal(self.threshold_percent) / Decimal(100)
        return amt >= threshold_amount

    def get_remaining_amount(self, current_amount: Decimal) -> Decimal:
        amt = self._validate_current_amount(current_amount)
        return self.limit_amount - amt

    def get_usage_percentage(self, current_amount: Decimal) -> float:
        amt = self._validate_current_amount(current_amount)
        # limit_amount 在初始化/更新时已保证 > 0
        return float((amt / self.limit_amount) * 100)

    def update_limit(self, new_limit: Decimal) -> None:
        # 更新也必须走同样的校验，防止对象后期进入非法状态
        self.limit_amount = self._validate_limit_amount(new_limit)

    def update_threshold(self, new_threshold: int) -> None:
        self.threshold_percent = self._validate_threshold(new_threshold)

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

    def to_dict(self) -> dict:
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
        category_info = f"category_id={self.category_id}" if self.category_id else "总预算"
        return (f"Budget(id={self.budget_id}, {category_info}, "
                f"period={self.period.value}, limit={self.limit_amount})")

    def __eq__(self, other) -> bool:
        if not isinstance(other, Budget):
            return False
        return self.budget_id == other.budget_id
