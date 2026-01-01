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
        查询账目条目（带输入校验）

        设计原则：
        - 对“参数组合明显不合法”的情况（如 start_date > end_date）直接抛 ValueError，避免静默返回空结果。
        - 对存量数据中单条记录字段异常（如 timestamp 无法解析）采取跳过，避免整个查询崩溃。
        """
        # -------- 参数校验 / 归一化（建议放在最前面） --------
        if start_date is not None and not isinstance(start_date, datetime):
            raise TypeError("start_date 必须是 datetime 或 None")
        if end_date is not None and not isinstance(end_date, datetime):
            raise TypeError("end_date 必须是 datetime 或 None")

        if start_date is not None and end_date is not None and start_date > end_date:
            raise ValueError("start_date 不能晚于 end_date")

        # 时区一致性：避免 naive/aware datetime 比较触发 TypeError
        # 约束：若 start/end 任一为 aware，则另一者也必须为 aware；并且后续 entry_time 也必须可比较
        if start_date is not None and end_date is not None:
            start_aware = start_date.tzinfo is not None
            end_aware = end_date.tzinfo is not None
            if start_aware != end_aware:
                raise ValueError("start_date 和 end_date 的 tzinfo 必须一致（要么都带时区，要么都不带）")

        # 金额参数：允许 Decimal / int / float / str 等可转换值，统一转为 Decimal
        def _to_decimal(x, name: str) -> Optional[Decimal]:
            if x is None:
                return None
            if isinstance(x, Decimal):
                return x
            try:
                # 用 str 包一层，避免 float 二进制表示直接进 Decimal
                return Decimal(str(x))
            except Exception as e:
                raise TypeError(f"{name} 无法转换为 Decimal: {e}")

        min_amount = _to_decimal(min_amount, "min_amount")
        max_amount = _to_decimal(max_amount, "max_amount")
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            raise ValueError("min_amount 不能大于 max_amount")

        # keyword：空字符串视为未提供
        if keyword is not None:
            if not isinstance(keyword, str):
                raise TypeError("keyword 必须是 str 或 None")
            keyword = keyword.strip()
            if keyword == "":
                keyword = None

        results: List[Entry] = []

        for entry_data in self.data['entries'].values():
            # -------- 用户ID过滤 --------
            if user_id and entry_data.get('user_id') != str(user_id):
                continue

            # -------- 分类ID过滤 --------
            if category_id:
                cat = entry_data.get('category') or {}
                if cat.get('category_id') != str(category_id):
                    continue

            # -------- 标签过滤（任一匹配即可）--------
            if tag_ids:
                entry_tag_ids = [tag.get('tag_id') for tag in entry_data.get('tags', []) if isinstance(tag, dict)]
                # entry_tag_ids 里可能有 None，直接用 membership 判断即可
                if not any(str(tag_id) in entry_tag_ids for tag_id in tag_ids):
                    continue

            # -------- 日期过滤 --------
            ts = entry_data.get('timestamp')
            if not ts:
                # 脏数据：没有时间戳，跳过
                continue
            try:
                entry_time = datetime.fromisoformat(ts)
            except ValueError:
                # 脏数据：timestamp 非法，跳过（也可改为 raise）
                continue

            # 若查询条件是 aware datetime，但 entry_time 是 naive（或反之），比较会 TypeError
            if start_date is not None:
                if (start_date.tzinfo is not None) != (entry_time.tzinfo is not None):
                    # 数据与条件时区形态不一致：跳过该条（也可改为 raise，视项目策略）
                    continue
                if entry_time < start_date:
                    continue
            if end_date is not None:
                if (end_date.tzinfo is not None) != (entry_time.tzinfo is not None):
                    continue
                if entry_time > end_date:
                    continue

            # -------- 金额过滤 --------
            amt_raw = entry_data.get('amount')
            if amt_raw is None:
                continue
            try:
                entry_amount = Decimal(str(amt_raw))
            except Exception:
                continue

            if min_amount is not None and entry_amount < min_amount:
                continue
            if max_amount is not None and entry_amount > max_amount:
                continue

            # -------- 关键词搜索（标题或备注）--------
            if keyword:
                title = (entry_data.get('title') or "")
                note = (entry_data.get('note') or "")
                keyword_lower = keyword.lower()
                if (keyword_lower not in title.lower() and keyword_lower not in note.lower()):
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
