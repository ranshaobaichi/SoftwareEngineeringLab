"""
标签模型
"""
import uuid
from typing import Optional


class Tag:
    """
    标签类 - 管理账目标签
    
    Attributes:
        tag_id: 标签唯一标识符
        name: 标签名称
        color: 标签颜色(可选)
        description: 标签描述(可选)
    """
    
    def __init__(
        self,
        name: str,
        color: Optional[str] = None,
        description: Optional[str] = None,
        tag_id: Optional[uuid.UUID] = None
    ):
        """
        初始化标签对象
        
        Args:
            name: 标签名称
            color: 标签颜色(可选)
            description: 标签描述(可选)
            tag_id: 标签ID(可选,默认自动生成)
        """
        self.tag_id = tag_id if tag_id else uuid.uuid4()
        self.name = name
        self.color = color or "#808080"  # 默认灰色
        self.description = description
    
    def rename(self, new_name: str) -> None:
        """
        重命名标签
        
        Args:
            new_name: 新的标签名称
        """
        if not new_name or not new_name.strip():
            raise ValueError("标签名称不能为空")
        self.name = new_name.strip()
    
    def update_color(self, new_color: str) -> None:
        """
        更新标签颜色
        
        Args:
            new_color: 新的颜色值(十六进制格式)
        """
        self.color = new_color
    
    def merge_with(self, other_tag: 'Tag') -> None:
        """
        将另一个标签合并到当前标签
        此方法主要用于标签管理,实际的数据迁移需要在数据库层面完成
        
        Args:
            other_tag: 要合并的标签
        """
        if not isinstance(other_tag, Tag):
            raise TypeError("只能合并Tag对象")
        # 合并后保留当前标签的ID和名称,但可以选择保留更详细的描述
        if not self.description and other_tag.description:
            self.description = other_tag.description
    
    def to_dict(self) -> dict:
        """
        将标签对象转换为字典
        
        Returns:
            标签信息字典
        """
        return {
            'tag_id': str(self.tag_id),
            'name': self.name,
            'color': self.color,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Tag':
        """
        从字典创建标签对象
        
        Args:
            data: 标签信息字典
            
        Returns:
            Tag对象
        """
        return cls(
            name=data['name'],
            color=data.get('color'),
            description=data.get('description'),
            tag_id=uuid.UUID(data['tag_id'])
        )
    
    def __repr__(self) -> str:
        """返回标签对象的字符串表示"""
        return f"Tag(id={self.tag_id}, name={self.name}, color={self.color})"
    
    def __eq__(self, other) -> bool:
        """判断两个标签对象是否相等"""
        if not isinstance(other, Tag):
            return False
        return self.tag_id == other.tag_id
    
    def __hash__(self) -> int:
        """返回标签对象的哈希值,用于集合操作"""
        return hash(self.tag_id)
