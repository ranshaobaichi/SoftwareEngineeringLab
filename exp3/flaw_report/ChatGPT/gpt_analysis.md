**PocketLedger 项目实现缺陷报告**

1. **文件: auth_service.py**  
   - 行 101-111：`change_password` 中仅检查新密码长度，未要求大小写/数字/特殊字符，密码强度校验过于薄弱，存在弱口令风险。  
   - 行 148-159：`_validate_phone` 中第一个 `return True` 直接导致后面的正则校验代码永久不可达，所有手机号都会被视为合法，输入校验形同虚设。  

2. **文件: user.py**  
   - 行 29-35：使用单次 SHA256 (`hashlib.sha256`) 对密码做哈希，无随机盐、无多轮迭代，也未使用专门密码哈希算法（如 PBKDF2/bcrypt），密码存储安全性不足，易被彩虹表/暴力破解。  
   - 行 75-93：`update_profile` 允许直接更新 `email`，但调用方 `AuthService.update_profile` 未重新验证邮箱格式、未校验邮箱唯一性，可能造成非法邮箱或重复邮箱写入数据库。  
   - 行 101-121：`from_dict` 直接还原 `password_hash`，但未记录哈希算法版本，未来若升级哈希算法将无法区分旧哈希与新哈希，影响向后兼容与安全迁移。  

3. **文件: database.py**  
   - 行 31-39：`__init__` 中数据库数据全部加载到内存，用 `json.dump` 全量写回，缺少并发写保护和原子写入，多个进程/实例同时操作同一 JSON 文件可能造成数据竞争和文件损坏。  
   - 行 42-55：`_load_from_file` 在 JSON 解析失败时仅打印警告并“使用空数据库”，未做备份/恢复策略，可能静默丢失全部原有数据。  
   - 行 57-66：`_save_to_file` 捕获异常后打印错误并 `raise`，但上层 `save_user`/`save_entry` 等方法均用 `try/except` 吞掉异常并返回 False，导致调用方无法得知具体错误原因，也无法区分 I/O 故障与业务失败。  
   - 行 83-105：`_init_default_categories` 仅在 `self.data['categories']` 为空时初始化，若文件中结构损坏但字段存在（如部分缺失/不完整），不会重新补充默认分类，恢复能力不足。  
   - 行 179-188：`query_entries` 中通过 `entry_data['timestamp']` 调用 `datetime.fromisoformat`，如果旧数据缺失该字段或格式不合法会抛异常，中断整个查询，缺少容错/跳过异常记录逻辑。  
   - 行 154-176：`delete_entry`/`delete_category`/`delete_tag` 仅做存在即删，未检查该分类/标签是否仍被其他条目引用，可能产生“悬挂引用”，破坏数据一致性。  
   - 行 240-246：`clear_all_data` 会直接清空所有数据后立即写回，未做任何确认或备份机制，如果被误调用将不可恢复地丢失所有用户数据。  

4. **文件: app_logic.py**  
   - 行 48-58：`delete_current_user` 仅调用 `database.delete_user` 删除用户和其 entries/budgets，没有显式删除与用户相关的 tags 或与标签绑定的条目中的引用，可能导致业务层逻辑与数据层约束不一致。  
   - 行 64-110：`add_entry` 中对 `amount`、`title`、`note` 等字段几乎不做业务校验（金额未校验为正数、标题未限制长度等），完全依赖上层 UI，若通过其他接口调用（如脚本/测试）易产生异常数据。  
   - 行 178-203：`add_tag_to_entry` 仅验证 entry/tag 存在，但不校验当前用户是否拥有该 entry/tag 的所有权，逻辑上允许跨用户篡改他人数据（只要拿到 id）。  
   - 行 212-238：`add_budget` 未检查同一用户同周期是否已存在预算，也未限制 `limit_amount` 为正，可能创建多条冲突预算或 0/负预算记录。  
   - 行 262-287：`get_summary_statistics` 将 `Decimal` 转为 `float`，在金额统计上引入二进制浮点误差，与内部统一使用 `Decimal` 的设计不一致。  

5. **文件: stat_engine.py**  
   - 行 42-64：`calculate_total_by_type` 统计总额时不区分货币（`entry.currency` 被忽略），多币种场景下会错误相加不同货币金额。  
   - 行 85-119：`get_statistics_by_category` 以“分类名称 string”作为 key 聚合，而不是以分类 ID 聚合，若存在多个同名分类会被错误合并，造成统计结果失真。  
   - 行 188-236：`get_monthly_statistics` 中月份循环固定 1-12，未对 `entries` 是否为空或年份是否在数据范围内做校验；所有月份都返回，即使无数据也返回 0 记录，接口语义与“实际存在的月份统计”可能不一致。  
   - 行 238-274：`get_top_expenses` 同样忽略货币字段，直接按金额排序，对多币种情况下“最大支出”结果不可靠。  
   - 行 276-329：`check_budget_status` 对分类预算和总预算仅按金额过滤，未考虑多币种，且对 `Budget.limit_amount == 0` 情况没有事前过滤，虽在 `get_usage_percentage` 特判，但 0 限额预算从业务上缺少防护。  

6. **文件: export_service.py**  
   - 行 35-91：`export_to_xlsx` 中对 `entry.note`、`entry.images` 直接使用，若模型实例中这些字段为 `None`/非列表（来自旧版本或脏数据），会在 `len(entry.images)` 等位置抛异常并导致整个导出失败，缺少字段级防御性编程。  
   - 行 93-137：`export_to_csv` 使用 `encoding='utf-8-sig'` 写入中文标题，但未在接口文档/注释中说明，调用方若按纯 UTF-8 处理可能出现 BOM 相关问题，编码策略与文档不一致。  
   - 行 139-214：`export_statistics_to_xlsx` 内部重新实例化 `StatEngine`，与 `AppLogic` 中的 `stat_engine` 重复构造，造成职责分散和维护成本增加；同时该方法直接依赖 `openpyxl` 和统计服务，违反单一职责与依赖倒置原则。  

7. **文件: ui_interface.py**  
   - 行 97-135：`ConsoleUI.show_entry_list` 直接调用 `entry.timestamp.strftime`，若从历史脏数据恢复出的 `timestamp` 非 `datetime` 类型会抛异常，缺少对于反序列化失败/类型不符的保护。  
   - 行 159-182：`ConsoleUI.show_budget_screen` 使用 `'period'`、`'limit_amount'` 等硬编码字典键，对 `get_budget_status` 返回字段结构高度耦合，一旦服务端字段变更（如改名/缺失）会直接抛异常，未做 `dict.get` 安全访问。  
   - 行 189-202：`show_message`、`confirm_dialog` 中使用 emoji 字符，在部分窄终端环境或不支持 emoji 编码的平台上可能导致显示错乱或编码错误，缺少降级策略。  

8. **文件: main.py**  
   - 行 23-31：`run` 方法主循环直接以同步 `input` 获取用户输入，缺少对 EOFError、KeyboardInterrupt 的捕获，用户 Ctrl+C 退出时可能留下不一致状态（未正常调用 `logout`）。  
   - 行 119-172：`_handle_view_entries` 中的删除逻辑通过用户输入的序号直接在当前内存 `entries` 列表上索引删除，若在高并发或多客户端场景下（虽然目前是 CLI），其他地方已删除该条目会导致“成功提示但实际上数据库中已无记录”的并发一致性问题。  
   - 行 206-258：`_handle_statistics` 对用户输入的统计时间范围（特别是“本月”逻辑）全部依赖本机系统时间，未校验用户自定义时区/系统时间错误的情况，可能导致统计范围偏移。  

9. **文件: `demo.py`**  
   - 行 33-63：`demo_basic_features` 使用硬编码 email/phone/password 注册固定账号 `"demo@example.com"`、`"13800138000"`，多次运行会因邮箱唯一约束失败；demo 未处理“已注册”情况而是简单打印结果，影响演示连贯性。  
   - 行 74-92：通过 `next(c for c in expense_categories if c.name == "餐饮")` 等硬编码名称查找分类，若默认分类名被用户修改或本地化，demo 将抛 `StopIteration` 异常导致整体演示中断。