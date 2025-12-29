"""User Model"""
import uuid
import hashlib
from typing import Optional
from datetime import datetime
from icontract import require, ensure


class User:
    """
    用户类 - 管理用户账户信息和认证
    
    Attributes:
        user_id: 用户唯一标识符
        email: 用户邮箱
        phone: 用户手机号
        password_hash: 密码哈希值
        nickname: 用户昵称
        avatar_path: 头像文件路径
        created_at: 账户创建时间
    """
    
    @require(lambda email: '@' in email and len(email) > 3)
    @require(lambda phone: len(phone) >= 8)
    @require(lambda password: len(password) >= 6)
    @require(lambda nickname: len(nickname.strip()) > 0)
    @ensure(lambda self: self.user_id is not None)
    @ensure(lambda self: len(self.password_hash) == 64)
    def __init__(
        self,
        email: str,
        phone: str,
        password: str,
        nickname: str,
        avatar_path: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None
    ):
        """
        初始化用户对象
        
        Args:
            email: 用户邮箱
            phone: 用户手机号
            password: 用户密码(明文,将被加密)
            nickname: 用户昵称
            avatar_path: 头像路径(可选)
            user_id: 用户ID(可选,默认自动生成)
        """
        self.user_id = user_id if user_id else uuid.uuid4()
        self.email = email
        self.phone = phone
        self.password_hash = self._hash_password(password)
        self.nickname = nickname
        self.avatar_path = avatar_path or "default_avatar.png"
        self.created_at = datetime.now()
    
    @require(lambda password: len(password) > 0)
    @ensure(lambda result: len(result) == 64)
    def _hash_password(self, password: str) -> str:
        """
        使用SHA256加密密码
        
        Args:
            password: 明文密码
            
        Returns:
            加密后的密码哈希值
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    @require(lambda password: len(password) > 0)
    @ensure(lambda result: len(result) == 64)
    def _hash_password_verify(self, password: str) -> str:
        """SHA256 hash for password (duplicate for contract)"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """
        验证密码是否正确
        
        Args:
            password: 待验证的密码
            
        Returns:
            密码是否正确
        """
        return self.password_hash == self._hash_password(password)
    
    @require(lambda old_password: len(old_password) > 0)
    @require(lambda new_password: len(new_password) >= 6)
    @ensure(lambda self, old_password, new_password, result: not result or self.verify_password(new_password))
    def update_password(self, old_password: str, new_password: str) -> bool:
        """
        Update password
        
        Args:
            old_password: Old password
            new_password: New password
            
        Returns:
            Whether update succeeded
        """
        if not self.verify_password(old_password):
            return False
        self.password_hash = self._hash_password(new_password)
        return True
    
    def update_profile(
        self,
        nickname: Optional[str] = None,
        avatar_path: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> None:
        """
        更新用户资料
        
        Args:
            nickname: 新昵称(可选)
            avatar_path: 新头像路径(可选)
            email: 新邮箱(可选)
            phone: 新手机号(可选)
        """
        if nickname:
            self.nickname = nickname
        if avatar_path:
            self.avatar_path = avatar_path
        if email:
            self.email = email
        if phone:
            self.phone = phone
    
    def to_dict(self) -> dict:
        """
        将用户对象转换为字典
        
        Returns:
            用户信息字典
        """
        return {
            'user_id': str(self.user_id),
            'email': self.email,
            'phone': self.phone,
            'password_hash': self.password_hash,
            'nickname': self.nickname,
            'avatar_path': self.avatar_path,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """
        从字典创建用户对象
        
        Args:
            data: 用户信息字典
            
        Returns:
            User对象
        """
        user = cls.__new__(cls)
        user.user_id = uuid.UUID(data['user_id'])
        user.email = data['email']
        user.phone = data['phone']
        user.password_hash = data['password_hash']
        user.nickname = data['nickname']
        user.avatar_path = data['avatar_path']
        user.created_at = datetime.fromisoformat(data['created_at'])
        return user
    
    def __repr__(self) -> str:
        """返回用户对象的字符串表示"""
        return f"User(id={self.user_id}, email={self.email}, nickname={self.nickname})"
    
    def __eq__(self, other) -> bool:
        """判断两个用户对象是否相等"""
        if not isinstance(other, User):
            return False
        return self.user_id == other.user_id
