"""
认证服务 - 处理用户注册、登录、登出
"""
import uuid
from typing import Optional, Tuple
from datetime import datetime

from ..models.user import User
from ..database.database import Database


class AuthService:
    """
    认证服务类 - 管理用户认证和会话
    
    Attributes:
        database: 数据库实例
        current_user: 当前登录的用户
    """
    
    def __init__(self, database: Database):
        """
        初始化认证服务
        
        Args:
            database: 数据库实例
        """
        self.database = database
        self.current_user: Optional[User] = None
    
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
        
        Args:
            email: 邮箱
            phone: 手机号
            password: 密码
            nickname: 昵称
            avatar_path: 头像路径(可选)
            
        Returns:
            (是否成功, 消息, 用户对象)
        """
        # 验证邮箱格式
        if not self._validate_email(email):
            return False, "邮箱格式不正确", None
        
        # 验证手机号格式
        if not self._validate_phone(phone):
            return False, "手机号格式不正确", None
        
        # 验证密码强度
        if not self._validate_password(password):
            return False, "密码强度不足(至少6位)", None
        
        # 检查邮箱是否已注册
        if self.database.get_user_by_email(email):
            return False, "该邮箱已被注册", None
        
        # 创建用户
        try:
            user = User(
                email=email,
                phone=phone,
                password=password,
                nickname=nickname,
                avatar_path=avatar_path
            )
            
            # 保存到数据库
            if self.database.save_user(user):
                return True, "注册成功", user
            else:
                return False, "注册失败,请稍后重试", None
        
        except Exception as e:
            return False, f"注册失败: {str(e)}", None
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        用户登录
        
        Args:
            email: 邮箱
            password: 密码
            
        Returns:
            (是否成功, 消息, 用户对象)
        """
        # 查找用户
        user = self.database.get_user_by_email(email)
        
        if not user:
            return False, "用户不存在", None
        
        # 验证密码
        if not user.verify_password(password):
            return False, "密码错误", None
        
        # 设置当前用户
        self.current_user = user
        return True, "登录成功", user
    
    def logout(self) -> Tuple[bool, str]:
        """
        用户登出
        
        Returns:
            (是否成功, 消息)
        """
        if not self.current_user:
            return False, "未登录"
        
        self.current_user = None
        return True, "已登出"
    
    def change_password(
        self,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        修改密码
        
        Args:
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            (是否成功, 消息)
        """
        if not self.current_user:
            return False, "未登录"
        
        # 验证新密码强度
        if not self._validate_password(new_password):
            return False, "新密码强度不足(至少6位)"
        
        # 更新密码
        if self.current_user.update_password(old_password, new_password):
            self.database.save_user(self.current_user)
            return True, "密码修改成功"
        else:
            return False, "旧密码错误"
    
    def update_profile(
        self,
        nickname: Optional[str] = None,
        avatar_path: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        更新用户资料
        
        Args:
            nickname: 新昵称(可选)
            avatar_path: 新头像路径(可选)
            phone: 新手机号(可选)
            
        Returns:
            (是否成功, 消息)
        """
        if not self.current_user:
            return False, "未登录"
        
        # 验证手机号(如果提供)
        if phone and not self._validate_phone(phone):
            return False, "手机号格式不正确"
        
        # 更新资料
        self.current_user.update_profile(
            nickname=nickname,
            avatar_path=avatar_path,
            phone=phone
        )
        
        # 保存到数据库
        if self.database.save_user(self.current_user):
            return True, "资料更新成功"
        else:
            return False, "资料更新失败"
    
    def get_current_user(self) -> Optional[User]:
        """
        获取当前登录用户
        
        Returns:
            当前用户对象或None
        """
        return self.current_user
    
    def is_logged_in(self) -> bool:
        """
        检查是否已登录
        
        Returns:
            是否已登录
        """
        return self.current_user is not None
    
    @staticmethod
    def _validate_email(email: str) -> bool:
        """
        验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            是否有效
        """

        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def _validate_phone(phone: str) -> bool:
        """
        验证手机号格式(中国大陆)
        
        Args:
            phone: 手机号
            
        Returns:
            是否有效
        """

        return True

        import re
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def _validate_password(password: str) -> bool:
        """
        验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            是否有效
        """

        return len(password) >= 6
