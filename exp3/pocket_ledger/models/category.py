"""
分类模型
"""
import uuid
from enum import Enum
from typing import Optional


class CategoryType(Enum):
    """分类类型枚举"""
    INCOME = "income"  # 收入
    EXPENSE = "expense"  # 支出


class Category:
    """
    分类类 - 管理账目分类
    
    Attributes:
        category_id: 分类唯一标识符
        name: 分类名称
        type: 分类类型(收入/支出)
        icon: 分类图标(可选)
        description: 分类描述(可选)
    """
    
    def __init__(
        self,
        name: str,
        category_type: CategoryType,
        icon: Optional[str] = None,
        description: Optional[str] = None,
        category_id: Optional[uuid.UUID] = None
    ):
        """
        初始化分类对象
        
        Args:
            name: 分类名称
            category_type: 分类类型
            icon: 分类图标(可选)
            description: 分类描述(可选)
            category_id: 分类ID(可选,默认自动生成)
        """
        self.category_id = category_id if category_id else uuid.uuid4()
        self.name = name
        self.type = category_type
        self.icon = icon
        self.description = description
    
    def rename(self, new_name: str) -> None:
        """
        重命名分类
        
        Args:
            new_name: 新的分类名称
        """
        if not new_name or not new_name.strip():
            raise ValueError("分类名称不能为空")
        self.name = new_name.strip()
    
    def update_icon(self, new_icon: str) -> None:
        """
        更新分类图标
        
        Args:
            new_icon: 新的图标名称或路径
        """
        self.icon = new_icon
    
    def update_description(self, new_description: str) -> None:
        """
        更新分类描述
        
        Args:
            new_description: 新的描述内容
        """
        self.description = new_description
    
    def to_dict(self) -> dict:
        """
        将分类对象转换为字典
        
        Returns:
            分类信息字典
        """
        return {
            'category_id': str(self.category_id),
            'name': self.name,
            'type': self.type.value,
            'icon': self.icon,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Category':
        """
        从字典创建分类对象
        
        Args:
            data: 分类信息字典
            
        Returns:
            Category对象
        """
        return cls(
            name=data['name'],
            category_type=CategoryType(data['type']),
            icon=data.get('icon'),
            description=data.get('description'),
            category_id=uuid.UUID(data['category_id'])
        )
    
    def __repr__(self) -> str:
        """返回分类对象的字符串表示"""
        return f"Category(id={self.category_id}, name={self.name}, type={self.type.value})"
    
    def __eq__(self, other) -> bool:
        """判断两个分类对象是否相等"""
        if not isinstance(other, Category):
            return False
        return self.category_id == other.category_id
