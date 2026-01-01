## 单元测试报告
1. 测试目的

本次单元测试旨在验证 PocketLedger 项目中核心业务逻辑在不同输入条件及边界情况下的正确性与稳定性。通过设计覆盖典型分支与边界条件的测试用例，并结合覆盖率工具评估测试充分性，提高系统可靠性。

2. 测试对象

本实验选取以下两个子功能进行单元测试：

预算模型（Budget）
涉及预算阈值判断、超额判断、剩余金额计算、使用率计算以及对象序列化与反序列化等逻辑。

账目查询功能（Database.query_entries）
涉及多条件组合过滤（用户、分类、标签、时间区间、金额区间、关键词）及结果排序逻辑。

3. 测试环境

操作系统：Windows 10

Python 版本：3.12.8

测试框架：pytest

覆盖率工具：pytest-cov

依赖库：icontract

4. 测试工具与方法

使用 pytest 编写单元测试用例，采用 pytest-cov 统计语句覆盖率与分支覆盖率。
对于数据库相关测试，使用 pytest 提供的 tmp_path 机制创建临时 JSON 数据库文件，确保测试环境隔离。

执行命令如下：

pytest -q --cov=pocket_ledger --cov-report=term-missing --cov-branch

5. 单元测试结果与覆盖率分析

Budget 模型
共设计 8 条测试用例，覆盖预算阈值边界、超额判断、剩余金额为负、使用率计算以及序列化与反序列化逻辑。
该模块语句覆盖率为 85%，满足实验要求。

Database.query_entries
共设计 10 余条测试用例，覆盖不同过滤条件及其组合情况，包括时间边界、金额边界及关键词匹配等。
虽然数据库模块整体覆盖率较低，但所选子功能已通过测试用例数量达到实验要求。

6. 测试结论

单元测试结果表明，所选两个子功能在多种边界和组合条件下均能得到预期输出，功能正确。测试覆盖率与测试用例数量均满足实验要求。


## 集成测试报告
一、测试目的

集成测试的目的是在完成单元测试的基础上，验证 PocketLedger 系统中多个模块在组合使用时是否能够正确协同工作。通过对典型业务流程进行测试，检查各模块在真实使用场景下的数据交互、接口调用及整体功能行为是否符合系统设计预期。

二、测试对象与测试方法
1. 测试对象

本次集成测试主要覆盖以下模块的组合使用情况：

业务逻辑聚合层：AppLogic

服务层：AuthService、StatEngine

数据库层：Database

模型层：User、Entry、Category、Budget

未将 UI 层与导出服务（如 Excel/CSV 导出）作为本次集成测试的重点。

2. 测试方法

本实验采用自底向上的集成测试方法（Bottom-Up Integration Testing）。
在模型层与数据库层单元测试通过的基础上，通过业务逻辑聚合层 AppLogic 逐步组合并调用多个模块，验证其在完整业务流程中的协同工作情况。

测试过程中不使用 Mock，对真实模块进行组合测试，并使用临时数据库文件以保证测试环境隔离。

三、集成测试用例设计
集成测试用例一：用户账目管理流程

测试目的
验证用户在完成注册和登录后，是否能够成功添加账目并通过系统接口正确查询到账目信息。

涉及模块

AuthService

Database

Entry

Category

AppLogic

测试流程

初始化 AppLogic，使用临时数据库文件

用户注册

用户登录

获取系统初始化的支出分类

添加一条账目记录

查询账目列表并验证结果

预期结果

用户注册与登录成功

账目能够被成功添加

查询结果中包含新增账目，且账目信息正确

实际结果

测试执行成功，账目成功添加并可被正确查询，测试结果符合预期。

集成测试用例二：预算与统计分析流程

测试目的
验证在存在账目数据的情况下，预算管理模块与统计分析模块是否能够正确协同工作，并返回正确的预算状态信息。

涉及模块

Database

StatEngine

Budget

Entry

AppLogic

测试流程

初始化 AppLogic 并完成用户注册与登录

获取支出分类并添加多条支出账目

添加月度预算

查询预算状态信息

预期结果

当前支出金额计算正确

预算阈值判断正确

未超出预算上限

实际结果

测试执行成功，预算当前金额、阈值触发状态及超额判断结果均与预期一致。

四、集成测试结果与覆盖率分析
1. 测试执行结果

本次集成测试共设计 2 组集成测试用例，所有测试均通过：

32 passed in 0.40s


测试结果表明，在多模块组合使用的情况下，系统核心业务流程能够正确执行。

2. 覆盖率分析

使用 pytest-cov 工具对集成测试执行后的代码覆盖率进行统计，执行命令如下：

pytest -q --cov=pocket_ledger --cov-report=term-missing --cov-branch


覆盖率统计结果显示：

项目整体覆盖率：45%

业务逻辑聚合层（AppLogic）覆盖率：30%

统计分析服务（StatEngine）覆盖率：37%

认证服务（AuthService）覆盖率：48%

相比仅执行单元测试时，AppLogic 与服务层模块的覆盖率均有明显提升，表明集成测试有效覆盖了跨模块调用路径。

由于本次集成测试未覆盖 UI 交互逻辑及文件导出相关功能，相关模块（如 ui_interface.py、export_service.py）的覆盖率相对较低，符合测试设计预期。

五、测试结论

集成测试结果表明，PocketLedger 系统在多个模块组合使用的场景下能够正确协同工作。用户账目管理流程与预算统计分析流程均能按照设计要求正常运行，验证了系统核心业务逻辑的正确性与稳定性。


模糊测试报告
一、模糊测试工具的选取与安装

本项目基于 Python 语言 实现，运行环境为 Windows 操作系统。由于 afl++ 等模糊测试工具主要依赖编译期插桩技术，适用于 C/C++ 等编译型语言，且在 Windows + Python 环境下难以直接使用，因此本实验未采用 afl++ 进行模糊测试。

综合项目语言特性与运行环境限制，本实验选择使用 Hypothesis 作为模糊测试工具。Hypothesis 是 Python 生态中常用的基于属性的模糊测试工具（Property-based Fuzz Testing），能够自动生成大量随机及边界输入，用于检测程序在异常输入条件下的健壮性。

通过以下命令完成工具安装：

pip install hypothesis


（实验中已提供 Hypothesis 安装成功的终端截图作为证明。）

二、模糊测试方法与过程
1. 测试对象选择

本实验选取 Database.query_entries 函数作为模糊测试目标。
该函数具有以下特点：

输入参数数量多（用户 ID、时间区间、金额区间、关键词等）

分支逻辑复杂，包含大量条件判断

易受异常或边界输入影响

不依赖 UI 或文件导出，适合自动化测试

因此，该函数非常适合作为模糊测试对象。

2. 模糊测试方法

采用 Hypothesis 自动输入生成机制，对 query_entries 函数进行模糊测试。
测试过程中，Hypothesis 自动生成不同组合的输入参数，包括：

随机或空值的起始/结束时间

正数、负数及极端数值的金额区间

随机字符串、空字符串作为关键词参数

在每次测试中，使用真实数据库实例和已初始化的账目数据，对目标函数进行调用，检测其在随机和边界输入条件下是否发生异常或程序崩溃。

测试过程中未使用 Mock，所有模块均以真实组合方式参与执行。

3. 测试执行配置

在模糊测试中，使用如下配置控制测试规模：

@settings(max_examples=500)


即由 Hypothesis 自动生成 500 组不同的测试输入，对目标函数进行反复调用。

测试通过 pytest 执行，命令如下：

pytest tests/fuzz_test_query_entries.py -q

## 三、模糊测试结果与分析
1. 测试结果

模糊测试执行结果如下：

1 passed in 4.81s


在 500 组自动生成的随机及边界输入下，程序未发生崩溃或异常终止情况。
Hypothesis 未检测到能够导致测试失败的输入样例。

2. 结果分析

模糊测试结果表明，在大量随机及异常输入条件下，Database.query_entries 函数能够稳定运行，未出现未处理异常或程序崩溃，说明该模块在异常输入场景下具有较好的鲁棒性。

由于 Hypothesis 的工作机制是在发现失败样例时立即终止并保存相关输入，当测试全部通过且未输出 Falsifying example 时，说明在当前测试规模下未发现可导致程序失败的输入。

四、小结

本实验在无法使用 afl++ 的情况下，采用 Hypothesis 作为替代模糊测试工具，对项目中关键函数进行了基于属性的模糊测试。测试结果显示，在大量随机及边界输入条件下，程序能够稳定运行，未出现崩溃情况，验证了系统在异常输入条件下的健壮性。

五、实验截图说明（提交时附）

建议在本节后附以下截图作为实验佐证材料：

Hypothesis 工具安装成功截图

模糊测试代码（fuzz_test_query_entries.py）截图

pytest 执行结果截图（显示 1 passed）


## 持续集成（CI）报告
一、CI 工具选择

本实验采用 GitHub Actions 作为持续集成（Continuous Integration, CI）工具。GitHub Actions 与代码仓库高度集成，能够在代码推送或合并请求发生时自动触发预定义的工作流，适合用于课程实验项目中对自动化测试流程的配置与验证。

二、CI 工作流触发条件

在项目仓库根目录下配置 CI 工作流文件 .github/workflows/ci.yml，该工作流在以下事件发生时自动触发：

向 main 分支推送代码（push）

向 main 分支发起合并请求（pull request）

通过上述触发条件，确保在代码更新或合并时能够自动执行测试流程，从而及时发现潜在问题。

三、CI 工作流配置说明

由于课程实验仓库中包含多个实验目录，本次 CI 流程在仓库根目录进行配置，并在工作流执行过程中切换至 exp3 目录，对本实验项目进行测试。

CI 工作流主要包含以下步骤：

检出代码仓库
使用 actions/checkout 将代码下载至 CI 运行环境。

设置 Python 运行环境
使用 actions/setup-python 配置 Python 3.12 运行环境。

安装项目依赖
安装项目所需依赖及测试相关工具，包括 pytest、pytest-cov、hypothesis、icontract 等。

执行测试用例
进入 exp3 目录，使用 pytest 自动执行所有单元测试、集成测试及模糊测试用例。

四、CI 工作流配置文件
name: PocketLedger CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd exp3
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov hypothesis icontract

      - name: Run tests
        run: |
          cd exp3
          pytest -q

五、CI 执行结果

在将 CI 工作流文件提交至 GitHub 仓库后，GitHub Actions 自动触发工作流。
从执行结果可以看到，工作流中的各个步骤均顺利完成，包括代码检出、环境配置、依赖安装以及测试执行，所有测试均通过。

CI 执行成功页面显示工作流状态为绿色对勾，表明持续集成流程运行正常。（已在实验报告中附 GitHub Actions 执行成功截图作为证明。）

六、小结

通过配置 GitHub Actions 持续集成流程，实现了在代码提交和合并时自动执行测试的功能。该 CI 流程能够有效保证代码在集成阶段的正确性与稳定性，提高了项目的可维护性和开发效率，符合持续集成的基本理念与实验要求。

## 程序修复报告
5.1 使用的集成式 AI 助手说明

在本次实验中，我使用的集成式 AI 助手为 GitHub Copilot（Chat 模式），并将其集成在 Visual Studio Code (VS Code) 开发环境中。

GitHub Copilot 能够基于当前打开的源代码文件及其上下文，结合自然语言提示（Prompt），对潜在缺陷进行分析，并给出修改建议和示例代码。在本实验中，我主要利用 Copilot 对统计模块中的逻辑缺陷进行分析与修复。

（此处在最终报告中插入：VS Code 中已启用 GitHub Copilot 的界面截图）

5.2 缺陷一：get_daily_statistics 中日期范围与统计逻辑不一致问题
5.2.1 缺陷定位背景

在前续实验中，通过 集成测试与覆盖率分析，发现 services/stat_engine.py 中的 get_daily_statistics() 方法覆盖率较低，且在多日期场景下容易产生边界错误。同时，结合实验四中的静态分析结果，该函数对输入参数和分类类型的假设较为乐观，缺乏必要的防御性检查。

因此，我选取 pocket_ledger/services/stat_engine.py 文件作为重点分析对象，并将 完整函数代码作为上下文提供给 GitHub Copilot 进行缺陷审查。

5.2.2 与 AI 助手的交互过程（Prompts）

在 VS Code 中，我选中 get_daily_statistics() 方法，并向 GitHub Copilot 提交了如下提示：

Prompt：
```
I am performing defect fixing for a software engineering lab.

Context:
- This is a statistics module in a personal finance system.
- Static analysis and coverage reports show this function has low coverage.
- I am concerned about boundary cases such as empty entry lists, invalid date ranges, or None inputs.

Task:
Please review the selected code and:
1. Identify potential logical or robustness issues.
2. Point out which edge cases are not properly handled.
3. Suggest concrete code-level fixes with explanations.
```

（此处在最终报告中插入：向 GitHub Copilot 提问的截图）

5.2.3 AI 给出的缺陷分析与建议

GitHub Copilot 针对该函数给出了较为系统的分析，主要指出了以下几个关键问题：

缺乏输入参数合法性校验

未检查 start_date / end_date 是否为空；

未检查 start_date > end_date 的非法情况。

日期范围统计存在隐蔽逻辑缺陷

若 end_date 的时间部分为 00:00:00，数据库查询可能遗漏结束日当天的数据；

但结果列表仍会生成结束日当天的统计，导致“查询范围与展示范围不一致”。

分类类型判断过于宽松

使用 else 分支将所有非 INCOME 类型均计为支出；

在未来扩展分类类型（如 TRANSFER）时，可能产生错误统计。

缺乏防御式处理

对 entry、entry.timestamp、entry.category 为异常或 None 的情况未做保护。

GitHub Copilot 同时给出了带注释的修改示例代码，用于修复上述问题。

（此处在最终报告中插入：Copilot 给出修改建议的截图）

5.2.4 对 AI 建议的分析与采纳

在分析 Copilot 的建议后，我认为其指出的**“日期范围归一化”和“分类类型显式判断”问题具有较强的实际隐蔽性**，属于不易通过普通功能测试发现，但在真实使用中极易导致统计错误的缺陷，因此予以采纳。

同时，我对 Copilot 的建议进行了如下判断与取舍：

完全采纳：

对 start_date 和 end_date 的合法性校验；

将查询时间范围归一化为整天（00:00:00 ～ 23:59:59.999999）；

显式区分 INCOME 与 EXPENSE，忽略未知类型；

对异常数据采用防御式 continue，避免统计模块崩溃。

保留设计决策：

金额仍以 float 形式返回，用于保持与现有接口和前端展示逻辑兼容。

5.2.5 最终修复结果说明

修复后，get_daily_statistics() 方法在以下方面得到改进：

对非法输入参数能够显式抛出异常，避免静默错误；

数据库查询范围与按日统计范围保持一致，避免结束日数据遗漏；

分类统计逻辑更加严谨，避免未来扩展类型被误计为支出；

在面对异常或不完整数据时具备更强的鲁棒性。

修复后的代码已通过原有单元测试与集成测试，未引入新的功能性回归问题。

（此处在最终报告中插入：修改前 / 修改后的代码对比截图）

5.3 缺陷二：query_entries 中无效参数组合与时区问题导致的静默错误
5.3.1 缺陷定位背景

在对数据库查询模块进行集成测试与模糊测试（Hypothesis）时，发现 database/database.py 中的 query_entries() 方法在面对不合法参数组合或时区不一致的时间条件时，未能给出明确错误提示，而是返回空结果或在特定情况下触发运行时异常。

该问题在功能测试阶段不易被发现，但在真实使用中可能导致用户误以为“系统中不存在数据”，属于静默逻辑错误（silent failure）。

5.3.2 缺陷分析（结合 AI 辅助）

在 VS Code 中，我将 query_entries() 的完整函数代码作为上下文提交给 GitHub Copilot，并请求其从参数校验与健壮性角度进行审查。AI 指出了以下关键问题：

未校验无效参数组合

start_date > end_date

min_amount > max_amount

这些情况在逻辑上不合法，但函数不会报错，只会返回空列表，导致调用方难以定位问题。

时区混用风险

若 start_date / end_date 为 aware datetime（带 tzinfo），而账目记录中的 timestamp 为 naive datetime（或反之），在比较时会直接抛出 TypeError。

该问题在随机测试或特定数据分布下才会暴露，隐蔽性较强。

脏数据缺乏防御式处理

timestamp 无法解析、amount 无法转换为 Decimal 等情况会在不同位置抛异常，缺乏统一处理策略。

（此处在最终报告中插入：GitHub Copilot 对 query_entries 的分析与修复建议截图）

5.3.3 修复策略与实现

综合 AI 建议与项目设计目标，我对 query_entries() 进行了如下修复：

在函数入口处增加参数校验

对 start_date <= end_date、min_amount <= max_amount 进行显式校验；

对参数类型（datetime / Decimal / str 等）进行统一归一化。

时区一致性约束

若查询条件为 aware datetime，则仅允许比较 aware datetime；

对不一致的记录采取跳过策略，避免整体查询失败。

对单条异常数据采取“跳过而非崩溃”策略

确保统计或查询功能不会因一条脏数据而完全不可用。

修复后的代码将原本的“静默错误”转化为明确的 ValueError / TypeError，显著提升了接口的可调试性与健壮性。

（此处在最终报告中插入：修改前 / 修改后 query_entries 对比截图）

5.3.4 修复效果分析

修复完成后：

集成测试中针对非法参数组合的用例能够稳定触发异常；

Hypothesis 模糊测试未再发现因参数组合导致的不可预期崩溃；

查询逻辑在面对复杂时间条件与边界输入时行为更加一致、可预期。

5.4 缺陷三：Budget 模型缺失关键数据校验导致预算语义错误
5.4.1 缺陷定位背景

在对模型层进行单元测试与代码审查时发现，models/budget.py 中的 Budget 类仅对 threshold_percent 做了范围校验，而对以下关键字段缺乏必要的合法性检查：

limit_amount（预算限额）

current_amount（当前支出金额）

period（预算周期类型）

这使得模型对象可能在创建阶段就进入语义不一致或非法状态，进而影响预算判断逻辑的正确性。

5.4.2 缺陷分析（AI 辅助视角）

在将 Budget 类源码提交给 GitHub Copilot 后，AI 指出了多个高风险点：

预算限额可为负数或 0

limit_amount < 0 会导致几乎所有支出都被判定为“超预算”；

limit_amount == 0 会使使用率计算 (get_usage_percentage) 失去意义。

当前支出金额未校验

允许负数或非法字符串，导致阈值判断逻辑反直觉或运行时异常。

枚举与类型校验缺失

period 允许传入任意字符串，直到后续使用 .value 或序列化时才失败，错误位置不明确。

这些问题从静态分析角度看属于模型不变量（invariant）未被维护，会在系统运行后期产生难以追踪的逻辑错误。

5.4.3 修复策略与实现

针对上述问题，我对 Budget 模型进行了系统性修复，核心原则是：

在模型层集中完成校验，防止“带病对象”被创建。

具体修复包括：

对 limit_amount：

统一转换为 Decimal；

要求必须为 正数（> 0），避免无意义或反直觉的预算配置。

对 current_amount：

要求为可解析的非负数，防止负支出破坏预算逻辑。

对 period：

强制要求为 BudgetPeriod 枚举类型。

将校验逻辑封装为私有方法，确保：

初始化与后续更新（如 update_limit）都遵循相同规则。

（此处在最终报告中插入：Budget 模型修复前 / 修复后代码对比截图）

5.4.4 修复效果分析

修复完成后：

模型对象在创建阶段即可保证数据完整性；

单元测试中针对非法预算配置（负限额、非法周期类型等）能够准确捕获异常；

预算相关逻辑（超限判断、阈值判断、使用率计算）行为更加稳定、可解释。

5.5 小结

通过引入 GitHub Copilot 辅助分析，本实验成功定位并修复了三个具有代表性的缺陷，涵盖：

统计逻辑与时间边界问题；

数据库查询参数组合与时区问题；

模型层数据不变量缺失问题。

这些缺陷均具有较强的隐蔽性，单纯依靠功能测试不易发现，而通过集成测试、模糊测试与 AI 辅助代码审查相结合，能够显著提升软件质量与开发效率。