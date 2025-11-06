# PocketLedger 记账软件

基于Python实现的个人记账软件，实现了完整的UML设计。

## 项目结构

```
pocket_ledger/
├── models/              # 数据模型层
│   ├── __init__.py
│   ├── user.py         # 用户模型
│   ├── entry.py        # 账目条目模型
│   ├── category.py     # 分类模型
│   ├── tag.py          # 标签模型
│   └── budget.py       # 预算模型
├── database/           # 数据库层
│   ├── __init__.py
│   └── database.py     # 数据持久化
├── services/           # 业务逻辑层
│   ├── __init__.py
│   ├── auth_service.py     # 认证服务
│   ├── stat_engine.py      # 统计引擎
│   └── export_service.py   # 导出服务
├── app_logic.py        # 应用逻辑层
├── ui_interface.py     # UI接口层
└── __init__.py
main.py                 # 主程序入口
```

## 功能特性

### 已实现功能

1. **用户管理**
   - 用户注册/登录/登出
   - 密码加密存储
   - 个人信息管理

2. **账目管理**
   - 添加/编辑/删除账目
   - 支持收入和支出分类
   - 支持标签管理
   - 支持图片附件
   - 账目查询和筛选

3. **分类管理**
   - 预设14种常用分类
   - 支持自定义分类
   - 收入/支出分类

4. **预算管理**
   - 支持日/周/月/年预算
   - 预算提醒功能
   - 预算使用情况统计

5. **数据统计**
   - 收支汇总统计
   - 分类统计
   - 月度/年度统计
   - 标签统计

6. **数据导出**
   - 导出为Excel格式
   - 导出为CSV格式
   - 支持自定义时间范围

## 技术实现

- **编程语言**: Python 3.7+
- **数据存储**: JSON文件
- **架构模式**: 分层架构(模型-服务-逻辑-界面)
- **代码风格**: 遵循PEP 8规范

## 安装依赖

```bash
# 基础运行不需要额外依赖

# 如需导出Excel功能,安装:
pip install openpyxl
```

## 使用方法

### 命令行界面

```bash
python main.py
```

### 作为模块使用

```python
from pocket_ledger import AppLogic

# 创建应用实例
app = AppLogic()

# 注册用户
success, msg, user = app.register(
    email="user@example.com",
    phone="13800138000",
    password="password123",
    nickname="用户"
)

# 登录
success, msg, user = app.login("user@example.com", "password123")

# 添加账目
from decimal import Decimal
from pocket_ledger.models.category import CategoryType

categories = app.get_categories_by_type(CategoryType.EXPENSE)
success, msg, entry = app.add_entry(
    category_id=categories[0].category_id,
    title="午餐",
    amount=Decimal("35.5"),
    note="公司食堂"
)

# 查询账目
entries = app.query_entries()

# 查看统计
stats = app.get_summary_statistics()
print(f"总收入: {stats['total_income']}")
print(f"总支出: {stats['total_expense']}")
```

## 代码统计

### 核心代码行数(不含注释和空行)

- models/user.py: ~140行
- models/entry.py: ~200行
- models/category.py: ~90行
- models/tag.py: ~100行
- models/budget.py: ~180行
- database/database.py: ~450行
- services/auth_service.py: ~200行
- services/stat_engine.py: ~280行
- services/export_service.py: ~180行
- app_logic.py: ~360行
- ui_interface.py: ~200行
- main.py: ~400行

**总计: 约2800+行核心业务代码**

## UML设计对应

### 类图实现
- ✅ User类: 用户管理
- ✅ Entry类: 账目条目
- ✅ Category类: 分类管理
- ✅ Tag类: 标签管理
- ✅ Budget类: 预算管理
- ✅ Database类: 数据持久化
- ✅ ExportService类: 导出服务

### 组件图实现
- ✅ UI层: ConsoleUI (CLI实现), GUIInterface (接口预留)
- ✅ AppLogic层: 应用逻辑整合
- ✅ Service层: AuthService, StatEngine, ExportService
- ✅ Database层: 数据访问和持久化

### 时序图实现
- ✅ 添加账目流程: User -> UI -> AppLogic -> Database -> StatEngine

### 用例图实现
- ✅ 注册/登录/管理个人信息
- ✅ 添加/编辑/删除账目
- ✅ 查看/筛选账单
- ✅ 查看统计
- ✅ 设置预算提醒
- ✅ 导出为Excel

## 扩展说明

### GUI界面实现
代码中预留了`GUIInterface`接口,可以使用以下框架实现:
- PyQt5/PyQt6
- Tkinter
- Kivy
- wxPython

### 数据库扩展
当前使用JSON文件存储,可以扩展为:
- SQLite
- MySQL
- PostgreSQL

只需修改`Database`类即可,接口保持不变。

## 许可证

MIT License

## 作者

软件工程实验3
