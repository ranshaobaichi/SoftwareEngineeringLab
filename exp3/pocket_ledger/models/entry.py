"""Entry Model"""
import uuid
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from icontract import require, ensure

from .category import Category
from .tag import Tag


class Entry:
    """
    账目条目类 - 管理单条收支记录
    
    Attributes:
        entry_id: 条目唯一标识符
        user_id: 所属用户ID
        category: 所属分类
        title: 账目标题
        amount: 金额
        currency: 货币类型
        note: 备注
        timestamp: 记账时间
        images: 附件图片路径列表
        tags: 标签列表
    """
    
    @require(lambda title: len(title.strip()) > 0)
    @require(lambda amount: Decimal(str(amount)) > 0)
    @require(lambda currency: len(currency) > 0)
    @ensure(lambda self: self.entry_id is not None)
    @ensure(lambda self: self.amount > 0)
    def __init__(
        self,
        user_id: uuid.UUID,
        category: Category,
        title: str,
        amount: Decimal,
        currency: str = "CNY",
        note: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        images: Optional[List[str]] = None,
        entry_id: Optional[uuid.UUID] = None
    ):
        """
        初始化账目条目对象
        
        Args:
            user_id: 用户ID
            category: 分类对象
            title: 账目标题
            amount: 金额
            currency: 货币类型(默认CNY)
            note: 备注(可选)
            timestamp: 记账时间(可选,默认当前时间)
            images: 图片列表(可选)
            entry_id: 条目ID(可选,默认自动生成)
        """
        self.entry_id = entry_id if entry_id else uuid.uuid4()
        self.user_id = user_id
        self.category = category
        self.title = title
        self.amount = Decimal(str(amount))  # 确保使用Decimal类型
        self.currency = currency
        self.note = note or ""
        self.timestamp = timestamp if timestamp else datetime.now()
        self.images = images if images else []
        self.tags: List[Tag] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_tag(self, tag: Tag) -> bool:
        """
        添加标签
        
        Args:
            tag: 要添加的标签对象
            
        Returns:
            是否添加成功
        """
        if not isinstance(tag, Tag):
            raise TypeError("必须是Tag对象")
        if tag in self.tags:
            return False  # 标签已存在
        self.tags.append(tag)
        self.updated_at = datetime.now()
        return True
    
    def remove_tag(self, tag: Tag) -> bool:
        """
        移除标签
        
        Args:
            tag: 要移除的标签对象
            
        Returns:
            是否移除成功
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
            return True
        return False
    
    def add_image(self, image_path: str) -> None:
        """
        添加图片附件
        
        Args:
            image_path: 图片文件路径
        """
        if image_path not in self.images:
            self.images.append(image_path)
            self.updated_at = datetime.now()
    
    def remove_image(self, image_path: str) -> bool:
        """
        移除图片附件
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            是否移除成功
        """
        if image_path in self.images:
            self.images.remove(image_path)
            self.updated_at = datetime.now()
            return True
        return False
    
    @require(lambda new_amount: Decimal(str(new_amount)) > 0)
    @ensure(lambda self: self.amount > 0)
    def update_amount(self, new_amount: Decimal) -> None:
        """
        Update amount
        
        Args:
            new_amount: New amount
        """
        self.amount = Decimal(str(new_amount))
        self.updated_at = datetime.now()
    
    def update_category(self, new_category: Category) -> None:
        """
        更新分类
        
        Args:
            new_category: 新分类对象
        """
        if not isinstance(new_category, Category):
            raise TypeError("必须是Category对象")
        self.category = new_category
        self.updated_at = datetime.now()
    
    def update_note(self, new_note: str) -> None:
        """
        更新备注
        
        Args:
            new_note: 新备注内容
        """
        self.note = new_note
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """
        将账目条目转换为字典
        
        Returns:
            条目信息字典
        """
        return {
            'entry_id': str(self.entry_id),
            'user_id': str(self.user_id),
            'category': self.category.to_dict(),
            'title': self.title,
            'amount': str(self.amount),
            'currency': self.currency,
            'note': self.note,
            'timestamp': self.timestamp.isoformat(),
            'images': self.images,
            'tags': [tag.to_dict() for tag in self.tags],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Entry':
        """
        从字典创建账目条目对象
        
        Args:
            data: 条目信息字典
            
        Returns:
            Entry对象
        """
        from .category import Category
        from .tag import Tag
        
        entry = cls(
            user_id=uuid.UUID(data['user_id']),
            category=Category.from_dict(data['category']),
            title=data['title'],
            amount=Decimal(data['amount']),
            currency=data['currency'],
            note=data.get('note'),
            timestamp=datetime.fromisoformat(data['timestamp']),
            images=data.get('images', []),
            entry_id=uuid.UUID(data['entry_id'])
        )
        
        # 恢复标签
        if 'tags' in data:
            entry.tags = [Tag.from_dict(tag_data) for tag_data in data['tags']]
        
        # 恢复时间戳
        if 'created_at' in data:
            entry.created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            entry.updated_at = datetime.fromisoformat(data['updated_at'])
        
        return entry
    
    def __repr__(self) -> str:
        """返回条目对象的字符串表示"""
        return (f"Entry(id={self.entry_id}, title={self.title}, "
                f"amount={self.amount} {self.currency}, "
                f"category={self.category.name})")
    
    def __eq__(self, other) -> bool:
        """判断两个条目对象是否相等"""
        if not isinstance(other, Entry):
            return False
        return self.entry_id == other.entry_id
