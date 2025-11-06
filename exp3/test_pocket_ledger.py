"""
单元测试
"""
import unittest
import os
from decimal import Decimal
from datetime import datetime

from pocket_ledger.models.user import User
from pocket_ledger.models.category import Category, CategoryType
from pocket_ledger.models.tag import Tag
from pocket_ledger.models.entry import Entry
from pocket_ledger.models.budget import Budget, BudgetPeriod
from pocket_ledger.database.database import Database
from pocket_ledger.services.auth_service import AuthService
from pocket_ledger.services.stat_engine import StatEngine


class TestUserModel(unittest.TestCase):
    """测试用户模型"""
    
    def test_user_creation(self):
        """测试用户创建"""
        user = User(
            email="test@example.com",
            phone="13800138000",
            password="password123",
            nickname="测试用户"
        )
        
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.nickname, "测试用户")
        self.assertIsNotNone(user.user_id)
    
    def test_password_verification(self):
        """测试密码验证"""
        user = User(
            email="test@example.com",
            phone="13800138000",
            password="password123",
            nickname="测试用户"
        )
        
        self.assertTrue(user.verify_password("password123"))
        self.assertFalse(user.verify_password("wrongpassword"))
    
    def test_password_update(self):
        """测试密码更新"""
        user = User(
            email="test@example.com",
            phone="13800138000",
            password="oldpass",
            nickname="测试用户"
        )
        
        result = user.update_password("oldpass", "newpass")
        self.assertTrue(result)
        self.assertTrue(user.verify_password("newpass"))
        self.assertFalse(user.verify_password("oldpass"))


class TestCategoryModel(unittest.TestCase):
    """测试分类模型"""
    
    def test_category_creation(self):
        """测试分类创建"""
        category = Category(
            name="餐饮",
            category_type=CategoryType.EXPENSE,
            icon="🍔"
        )
        
        self.assertEqual(category.name, "餐饮")
        self.assertEqual(category.type, CategoryType.EXPENSE)
    
    def test_category_rename(self):
        """测试分类重命名"""
        category = Category("测试", CategoryType.EXPENSE)
        category.rename("新名称")
        self.assertEqual(category.name, "新名称")


class TestEntryModel(unittest.TestCase):
    """测试账目模型"""
    
    def setUp(self):
        """设置测试环境"""
        self.user = User(
            email="test@example.com",
            phone="13800138000",
            password="password123",
            nickname="测试用户"
        )
        self.category = Category("餐饮", CategoryType.EXPENSE)
    
    def test_entry_creation(self):
        """测试账目创建"""
        entry = Entry(
            user_id=self.user.user_id,
            category=self.category,
            title="午餐",
            amount=Decimal("35.5"),
            note="公司食堂"
        )
        
        self.assertEqual(entry.title, "午餐")
        self.assertEqual(entry.amount, Decimal("35.5"))
        self.assertEqual(entry.category.name, "餐饮")
    
    def test_tag_management(self):
        """测试标签管理"""
        entry = Entry(
            user_id=self.user.user_id,
            category=self.category,
            title="午餐",
            amount=Decimal("35.5")
        )
        
        tag = Tag("必需", "#FF0000")
        
        # 添加标签
        result = entry.add_tag(tag)
        self.assertTrue(result)
        self.assertIn(tag, entry.tags)
        
        # 重复添加应该失败
        result = entry.add_tag(tag)
        self.assertFalse(result)
        
        # 移除标签
        result = entry.remove_tag(tag)
        self.assertTrue(result)
        self.assertNotIn(tag, entry.tags)


class TestBudgetModel(unittest.TestCase):
    """测试预算模型"""
    
    def setUp(self):
        """设置测试环境"""
        self.user = User(
            email="test@example.com",
            phone="13800138000",
            password="password123",
            nickname="测试用户"
        )
    
    def test_budget_creation(self):
        """测试预算创建"""
        budget = Budget(
            user_id=self.user.user_id,
            period=BudgetPeriod.MONTHLY,
            limit_amount=Decimal("3000.0"),
            threshold_percent=80
        )
        
        self.assertEqual(budget.limit_amount, Decimal("3000.0"))
        self.assertEqual(budget.threshold_percent, 80)
    
    def test_budget_exceeded(self):
        """测试预算超限检查"""
        budget = Budget(
            user_id=self.user.user_id,
            period=BudgetPeriod.MONTHLY,
            limit_amount=Decimal("1000.0")
        )
        
        self.assertFalse(budget.is_exceeded(Decimal("500.0")))
        self.assertTrue(budget.is_exceeded(Decimal("1500.0")))
    
    def test_threshold_reached(self):
        """测试阈值检查"""
        budget = Budget(
            user_id=self.user.user_id,
            period=BudgetPeriod.MONTHLY,
            limit_amount=Decimal("1000.0"),
            threshold_percent=80
        )
        
        self.assertFalse(budget.is_threshold_reached(Decimal("500.0")))
        self.assertTrue(budget.is_threshold_reached(Decimal("800.0")))


class TestAuthService(unittest.TestCase):
    """测试认证服务"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_db = "test_auth.json"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        
        self.db = Database(self.test_db)
        self.auth = AuthService(self.db)
    
    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_register(self):
        """测试注册"""
        success, msg, user = self.auth.register(
            email="test@example.com",
            phone="13800138000",
            password="password123",
            nickname="测试用户"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(user)
    
    def test_login(self):
        """测试登录"""
        # 先注册
        self.auth.register(
            email="test@example.com",
            phone="13800138000",
            password="password123",
            nickname="测试用户"
        )
        
        # 登录
        success, msg, user = self.auth.login("test@example.com", "password123")
        self.assertTrue(success)
        self.assertEqual(self.auth.current_user.email, "test@example.com")


def run_tests():
    """运行所有测试"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
