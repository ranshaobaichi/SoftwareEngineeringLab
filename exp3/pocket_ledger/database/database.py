"""
数据库管理类 - 使用JSON文件存储数据
"""
import json
import os
import uuid
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from decimal import Decimal

from ..models.user import User
from ..models.entry import Entry
from ..models.category import Category, CategoryType
from ..models.tag import Tag
from ..models.budget import Budget


class Database:
    """
    数据库类 - 负责数据的持久化存储和查询
    使用JSON文件作为存储介质
    
    Attributes:
        db_path: 数据库文件路径
        data: 内存中的数据字典
    """
    
    def __init__(self, db_path: str = "pocket_ledger.json"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.data: Dict[str, Any] = {
            'users': {},
            'entries': {},
            'categories': {},
            'tags': {},
            'budgets': {}
        }
        self._load_from_file()
        self._init_default_categories()
    
    def _load_from_file(self) -> None:
        """从文件加载数据"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                print(f"警告: 无法解析数据库文件 {self.db_path}, 使用空数据库")
            except Exception as e:
                print(f"警告: 加载数据库文件时出错: {e}")
    
    def _save_to_file(self) -> None:
        """保存数据到文件"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"错误: 保存数据库文件时出错: {e}")
            raise
    
    def _init_default_categories(self) -> None:
        """初始化默认分类"""
        if not self.data['categories']:
            default_categories = [
                # 支出分类
                ('餐饮', CategoryType.EXPENSE, '🍔'),
                ('购物', CategoryType.EXPENSE, '🛍️'),
                ('交通', CategoryType.EXPENSE, '🚗'),
                ('娱乐', CategoryType.EXPENSE, '🎮'),
                ('医疗', CategoryType.EXPENSE, '💊'),
                ('教育', CategoryType.EXPENSE, '📚'),
                ('住房', CategoryType.EXPENSE, '🏠'),
                ('通讯', CategoryType.EXPENSE, '📱'),
                ('其他支出', CategoryType.EXPENSE, '💸'),
                # 收入分类
                ('工资', CategoryType.INCOME, '💰'),
                ('奖金', CategoryType.INCOME, '🎁'),
                ('投资收益', CategoryType.INCOME, '📈'),
                ('兼职', CategoryType.INCOME, '💼'),
                ('其他收入', CategoryType.INCOME, '💵'),
            ]
            
            for name, cat_type, icon in default_categories:
                category = Category(name=name, category_type=cat_type, icon=icon)
                self.data['categories'][str(category.category_id)] = category.to_dict()
            
            self._save_to_file()
    
    # ========== 用户相关操作 ==========
    
    def save_user(self, user: User) -> bool:
        """
        保存用户
        
        Args:
            user: 用户对象
            
        Returns:
            是否保存成功
        """
        try:
            self.data['users'][str(user.user_id)] = user.to_dict()
            self._save_to_file()
            return True
        except Exception as e:
            print(f"保存用户失败: {e}")
            return False
    
    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        通过ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户对象或None
        """
        user_data = self.data['users'].get(str(user_id))
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        通过邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            用户对象或None
        """
        for user_data in self.data['users'].values():
            if user_data['email'] == email:
                return User.from_dict(user_data)
        return None
    
    def delete_user(self, user_id: uuid.UUID) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        user_id_str = str(user_id)
        if user_id_str not in self.data['users']:
            return False

        # 删除用户记录
        del self.data['users'][user_id_str]

        # 收集并删除该用户的所有账目条目
        entries_to_delete = [
            eid for eid, ed in self.data['entries'].items()
            if ed.get('user_id') == user_id_str
        ]
        for eid in entries_to_delete:
            del self.data['entries'][eid]

        # 删除该用户的预算
        budgets_to_delete = [
            bid for bid, bd in self.data['budgets'].items()
            if bd.get('user_id') == user_id_str
        ]
        for bid in budgets_to_delete:
            del self.data['budgets'][bid]

        # 持久化并返回成功
        self._save_to_file()
        return True
    
    # ========== 账目条目相关操作 ==========
    
    def save_entry(self, entry: Entry) -> bool:
        """
        保存账目条目
        
        Args:
            entry: 账目条目对象
            
        Returns:
            是否保存成功
        """
        try:
            self.data['entries'][str(entry.entry_id)] = entry.to_dict()
            self._save_to_file()
            return True
        except Exception as e:
            print(f"保存账目失败: {e}")
            return False
    
    def get_entry_by_id(self, entry_id: uuid.UUID) -> Optional[Entry]:
        """
        通过ID获取账目条目
        
        Args:
            entry_id: 条目ID
            
        Returns:
            条目对象或None
        """
        entry_data = self.data['entries'].get(str(entry_id))
        if entry_data:
            return Entry.from_dict(entry_data)
        return None
    
    def delete_entry(self, entry_id: uuid.UUID) -> bool:
        """
        删除账目条目
        
        Args:
            entry_id: 条目ID
            
        Returns:
            是否删除成功
        """
        entry_id_str = str(entry_id)
        if entry_id_str in self.data['entries']:
            del self.data['entries'][entry_id_str]
            self._save_to_file()
            return True
        return False
    
    def query_entries(
        self,
        user_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
        tag_ids: Optional[List[uuid.UUID]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        keyword: Optional[str] = None
    ) -> List[Entry]:
        """
        查询账目条目
        
        Args:
            user_id: 用户ID过滤
            category_id: 分类ID过滤
            tag_ids: 标签ID列表过滤
            start_date: 起始日期过滤
            end_date: 结束日期过滤
            min_amount: 最小金额过滤
            max_amount: 最大金额过滤
            keyword: 关键词搜索(标题或备注)
            
        Returns:
            符合条件的条目列表
        """
        results = []
        
        for entry_data in self.data['entries'].values():
            # 用户ID过滤
            if user_id and entry_data['user_id'] != str(user_id):
                continue
            
            # 分类ID过滤
            if category_id and entry_data['category']['category_id'] != str(category_id):
                continue
            
            # 标签过滤
            if tag_ids:
                entry_tag_ids = [tag['tag_id'] for tag in entry_data.get('tags', [])]
                if not any(str(tag_id) in entry_tag_ids for tag_id in tag_ids):
                    continue
            
            # 日期过滤
            entry_time = datetime.fromisoformat(entry_data['timestamp'])
            if start_date and entry_time < start_date:
                continue
            if end_date and entry_time > end_date:
                continue
            
            # 金额过滤
            entry_amount = Decimal(entry_data['amount'])
            if min_amount and entry_amount < min_amount:
                continue
            if max_amount and entry_amount > max_amount:
                continue
            
            # 关键词搜索
            if keyword:
                keyword_lower = keyword.lower()
                if (keyword_lower not in entry_data['title'].lower() and
                    keyword_lower not in entry_data.get('note', '').lower()):
                    continue
            
            results.append(Entry.from_dict(entry_data))
        
        # 按时间倒序排序
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results
    
    # ========== 分类相关操作 ==========
    
    def save_category(self, category: Category) -> bool:
        """
        保存分类
        
        Args:
            category: 分类对象
            
        Returns:
            是否保存成功
        """
        try:
            self.data['categories'][str(category.category_id)] = category.to_dict()
            self._save_to_file()
            return True
        except Exception as e:
            print(f"保存分类失败: {e}")
            return False
    
    def get_category_by_id(self, category_id: uuid.UUID) -> Optional[Category]:
        """
        通过ID获取分类
        
        Args:
            category_id: 分类ID
            
        Returns:
            分类对象或None
        """
        category_data = self.data['categories'].get(str(category_id))
        if category_data:
            return Category.from_dict(category_data)
        return None
    
    def get_all_categories(self) -> List[Category]:
        """
        获取所有分类
        
        Returns:
            分类列表
        """
        return [Category.from_dict(data) for data in self.data['categories'].values()]
    
    def get_categories_by_type(self, category_type: CategoryType) -> List[Category]:
        """
        获取指定类型的分类
        
        Args:
            category_type: 分类类型
            
        Returns:
            分类列表
        """
        return [
            Category.from_dict(data)
            for data in self.data['categories'].values()
            if data['type'] == category_type.value
        ]
    
    def delete_category(self, category_id: uuid.UUID) -> bool:
        """
        删除分类
        
        Args:
            category_id: 分类ID
            
        Returns:
            是否删除成功
        """
        category_id_str = str(category_id)
        if category_id_str in self.data['categories']:
            del self.data['categories'][category_id_str]
            self._save_to_file()
            return True
        return False
    
    # ========== 标签相关操作 ==========
    
    def save_tag(self, tag: Tag) -> bool:
        """
        保存标签
        
        Args:
            tag: 标签对象
            
        Returns:
            是否保存成功
        """
        try:
            self.data['tags'][str(tag.tag_id)] = tag.to_dict()
            self._save_to_file()
            return True
        except Exception as e:
            print(f"保存标签失败: {e}")
            return False
    
    def get_tag_by_id(self, tag_id: uuid.UUID) -> Optional[Tag]:
        """
        通过ID获取标签
        
        Args:
            tag_id: 标签ID
            
        Returns:
            标签对象或None
        """
        tag_data = self.data['tags'].get(str(tag_id))
        if tag_data:
            return Tag.from_dict(tag_data)
        return None
    
    def get_all_tags(self) -> List[Tag]:
        """
        获取所有标签
        
        Returns:
            标签列表
        """
        return [Tag.from_dict(data) for data in self.data['tags'].values()]
    
    def delete_tag(self, tag_id: uuid.UUID) -> bool:
        """
        删除标签
        
        Args:
            tag_id: 标签ID
            
        Returns:
            是否删除成功
        """
        tag_id_str = str(tag_id)
        if tag_id_str in self.data['tags']:
            del self.data['tags'][tag_id_str]
            self._save_to_file()
            return True
        return False
    
    # ========== 预算相关操作 ==========
    
    def save_budget(self, budget: Budget) -> bool:
        """
        保存预算
        
        Args:
            budget: 预算对象
            
        Returns:
            是否保存成功
        """
        try:
            self.data['budgets'][str(budget.budget_id)] = budget.to_dict()
            self._save_to_file()
            return True
        except Exception as e:
            print(f"保存预算失败: {e}")
            return False
    
    def get_budget_by_id(self, budget_id: uuid.UUID) -> Optional[Budget]:
        """
        通过ID获取预算
        
        Args:
            budget_id: 预算ID
            
        Returns:
            预算对象或None
        """
        budget_data = self.data['budgets'].get(str(budget_id))
        if budget_data:
            return Budget.from_dict(budget_data)
        return None
    
    def get_budgets_by_user(self, user_id: uuid.UUID) -> List[Budget]:
        """
        获取用户的所有预算
        
        Args:
            user_id: 用户ID
            
        Returns:
            预算列表
        """
        return [
            Budget.from_dict(data)
            for data in self.data['budgets'].values()
            if data['user_id'] == str(user_id)
        ]
    
    def delete_budget(self, budget_id: uuid.UUID) -> bool:
        """
        删除预算
        
        Args:
            budget_id: 预算ID
            
        Returns:
            是否删除成功
        """
        budget_id_str = str(budget_id)
        if budget_id_str in self.data['budgets']:
            del self.data['budgets'][budget_id_str]
            self._save_to_file()
            return True
        return False
    
    def clear_all_data(self) -> None:
        """清空所有数据(危险操作!)"""
        self.data = {
            'users': {},
            'entries': {},
            'categories': {},
            'tags': {},
            'budgets': {}
        }
        self._save_to_file()
        self._init_default_categories()
