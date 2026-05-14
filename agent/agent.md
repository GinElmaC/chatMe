# ChatMe Agent 文档

## 项目概述

**ChatMe** (中文名：千语) 是一个具有记忆功能的AI女友聊天程序，通过与LLM（DeepSeek/OpenAI）的交互，实现从陌生人到亲密关系的情感递进式聊天体验。

### 最新特性（v2.0）
- **新记忆系统**：每日聊天记录 + 集中浓缩历史
- **SummaryAgent**：专门负责浓缩聊天记录和更新用户印象
- **用户印象管理**：跟踪用户的性格、偏好、重要日期等
- **程序退出时浓缩**：自动触发浓缩流程

---

## 核心设计理念

- **情感递进**：从陌生→熟悉→有好感→亲密→交往的5个关系等级
- **记忆系统**：持久化聊天记录、人格设定、浓缩历史和用户印象
- **真实感**：打字延迟、主动对话、追问功能等模拟真人交互
- **成长系统**：经验值、好感度、关系升级等激励机制
- **每日记录**：按日期保存完整聊天记录，无大小限制
- **智能浓缩**：自动生成每日摘要，提取核心事件，更新用户印象

---

## 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py                                  │
│                    (主程序入口)                                  │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├───────────────┬───────────────┬───────────────────┐
         ↓               ↓               ↓                   ↓
┌──────────────────┐ ┌──────────┐ ┌───────────┐ ┌───────────────────┐
│  MemoryManager   │ │LLMClient │ │ Scheduler │ │   SummaryAgent    │
│  (记忆管理器)    │ │(AI交互)  │ │(调度器)   │ │ (浓缩Agent)       │
└────────┬─────────┘ └──────────┘ └─────┬─────┘ └─────────┬─────────┘
         │                               │                 │
         │                               │                 │
         │                               │                 │
         └──────────────────┬────────────┴─────────────────┘
                            ↓
                     ┌──────────────┐
                     │    数据层    │
                     └──────────────┘
                     ├─ data/
                     │  ├─ chat_history/
                     │  │  ├─ chat_history_2026-05-14.json
                     │  │  └─ chat_history_2026-05-13.json
                     │  ├─ personality/
                     │  │  └─ personality.json
                     │  ├─ chat_history_zip.json (浓缩历史)
                     │  ├─ user_impression.json (用户印象)
                     │  └─ system_config.json (系统配置)
```

---

## 核心文件功能说明

### 1. main.py - 主程序入口

**职责**：
- 程序启动和初始化
- 主聊天循环
- 用户输入处理
- 退出时自动浓缩触发

**核心功能**：
- 加载环境变量和配置
- 初始化四大核心组件：`MemoryManager`、`LLMClient`、`Scheduler`、`SummaryAgent`
- 处理首次聊天问候
- 监听用户输入（支持 `退出`、`浓缩`、`状态` 等命令）
- 主动消息显示线程
- atexit 钩子：程序退出时自动触发浓缩
- 异常处理和资源清理

**关键代码结构**：
```python
main()
├── 初始化组件
│   ├── MemoryManager (新记忆管理)
│   ├── LLMClient (AI交互)
│   ├── Scheduler (定时任务)
│   └── SummaryAgent (浓缩Agent)
├── 首次聊天检测（今日聊天记录）
├── 主动消息线程
├── atexit注册（退出时浓缩）
└── 主聊天循环
    ├── 用户输入
    ├── 命令处理（浓缩/状态/退出）
    ├── 经验值/好感度更新
    ├── LLM对话（含浓缩历史+印象）
    └── 打字模拟
```

**新增命令**：
| 命令 | 功能 |
|------|------|
| `浓缩` / `summary` / `总结` | 立即触发浓缩流程 |
| `状态` / `stats` | 显示当前状态和统计信息 |

---

### 2. src/memory_manager.py - 记忆管理模块（新系统）

**核心类**：`MemoryManager`

**职责**：
- 数据持久化管理
- 每日聊天记录存取
- 浓缩历史管理
- 用户印象管理
- 人格设定管理
- 关系等级与经验值系统

**核心数据结构**：

| 关系等级 | 经验值阈值 | 等级名称 | 特点 |
|---------|-----------|---------|------|
| 0 | 0-29 | 陌生 | 刚认识，保持礼貌 |
| 1 | 30-99 | 熟悉 | 像好朋友 |
| 2 | 100-299 | 有好感 | 可以更亲近 |
| 3 | 300-599 | 亲密 | 很亲密，像恋人 |
| 4 | 600+ | 交往 | 完全放开 |

**文件结构**：
```
data/
├── chat_history/
│   ├── chat_history_YYYY-MM-DD.json  # 每日聊天记录
│   └── ...
├── personality/
│   └── personality.json             # 人格设定
├── chat_history_zip.json            # 浓缩历史（新）
├── user_impression.json             # 用户印象（新）
└── system_config.json               # 系统配置（新）
```

**chat_history_zip.json 格式**：
```json
{
  "summaries": [
    {
      "date": "2026-05-14",
      "summary": "对话摘要内容...",
      "timestamp": "2026-05-14T23:59:59"
    }
  ],
  "core_events": [
    "核心事件1",
    "核心事件2"
  ]
}
```

**user_impression.json 格式**：
```json
{
  "description": "用户的综合描述",
  "traits": ["性格特点1", "性格特点2"],
  "preferences": ["用户偏好1", "用户偏好2"],
  "important_dates": ["重要日期1", "重要日期2"],
  "goals": ["目标1", "目标2"],
  "updated_at": "2026-05-14T23:59:59"
}
```

**system_config.json 格式**：
```json
{
  "last_summary_date": "2026-05-13",
  "created_at": "2026-05-14T00:00:00"
}
```

**主要方法**：

| 方法名 | 功能 |
|-------|------|
| `load_chat_history_by_date(date)` | 加载指定日期的聊天记录 |
| `load_today_chat_history()` | 加载今日聊天记录 |
| `save_today_chat_history(history)` | 保存今日聊天记录 |
| `add_chat_message(role, content)` | 添加消息，自动+1经验 |
| `load_zip_history()` | 加载浓缩历史 |
| `save_zip_history(data)` | 保存浓缩历史 |
| `add_to_zip_history(date, summary, events)` | 添加到浓缩历史 |
| `load_user_impression()` | 加载用户印象 |
| `save_user_impression(impression)` | 保存用户印象 |
| `load_personality()` | 加载人格设定（含缓存） |
| `get_context_messages(limit)` | 获取LLM上下文（含摘要、事件、印象） |
| `get_uncompressed_dates()` | 获取未浓缩的日期列表 |
| `get_stats()` | 获取统计信息 |
| `add_content_bonus(score)` | 根据内容评分加减经验 |
| `get_relationship_level()` | 获取当前等级 |

**向后兼容方法**：
| 方法名 | 说明 |
|-------|------|
| `load_chat_history()` | 等价于 load_today_chat_history() |
| `load_summarized_memory()` | 返回浓缩历史中的 summaries |
| `add_summarized_memory()` | 空操作（新系统不使用） |
| `clear_chat_history()` | 空操作（新系统不使用） |

---

### 3. src/llm_client.py - LLM交互模块

**核心类**：`LLMClient`

**职责**：
- 与DeepSeek/OpenAI API通信
- 构建系统提示词
- 生成对话回复
- 聊天摘要生成
- 情感分析（好感度评分）
- 打字延迟计算

**系统提示词构建**：
根据人格设定和关系等级动态生成，包含：
- 角色信息（姓名、年龄、地点等）
- 性格特点
- 当前关系等级
- 亲密程度要求
- 回复风格指导

**主要方法**：

| 方法名 | 功能 |
|-------|------|
| `chat_with_typing_delay(messages, personality, stream)` | 获取回复（stream=True时添加系统提示词） |
| `chat_stream(messages, personality)` | 流式对话 |
| `chat(messages, personality)` | 普通对话 |
| `summarize_chat(chat_history)` | 生成聊天摘要 |
| `analyze_content_sentiment(user_message)` | 分析用户消息情感，返回-5~+5分 |
| `calculate_typing_delay(text)` | 计算打字时间（汉字0.5秒/字） |
| `get_chinese_count(text)` | 计算汉字数量 |

**chat_with_typing_delay 新增参数**：
- `stream=True`（默认）：添加系统提示词，用于正常聊天
- `stream=False`：不添加系统提示词，用于SummaryAgent的分析任务

---

### 4. src/scheduler.py - 定时任务调度器

**核心类**：`Scheduler`

**职责**：
- 后台定时任务管理
- 主动对话生成
- 追问功能
- 打字状态管理

**三大后台线程**：

1. **配置重载线程**（每60秒）
   - 重新加载人格设定
   - 重新加载浓缩历史

2. **每日摘要线程**（保留，空循环）
   - 新系统已废弃，在程序退出时浓缩

3. **主动对话线程**（核心）
   - 根据关系等级计算主动消息间隔
   - 8:00-24:00为活跃时间
   - 支持追问功能
   - 打字状态管理

**主动消息间隔**（根据等级）：

| 等级 | 最小间隔 | 最大间隔 |
|-----|---------|---------|
| 0（陌生） | 60分钟 | 240分钟 |
| 1（熟悉） | 45分钟 | 180分钟 |
| 2（有好感）| 30分钟 | 150分钟 |
| 3（亲密） | 20分钟 | 120分钟 |
| 4（交往） | 10分钟 | 90分钟 |

**追问机制**：
| 等级 | 追问等待 | 最多追问 |
|-----|---------|---------|
| 0（陌生） | 60分钟 | 1次 |
| 1（熟悉） | 45分钟 | 1次 |
| 2（有好感）| 30分钟 | 2次 |
| 3（亲密） | 20分钟 | 2次 |
| 4（交往） | 15分钟 | 3次 |

- 等级越高，追问越频繁
- 第二次及以后追问扣2点经验值
- 达到最大次数后停止

**主要方法**：

| 方法名 | 功能 |
|-------|------|
| `start()` | 启动后台线程 |
| `stop()` | 停止后台线程 |
| `start_typing(text)` | 开始打字状态 |
| `end_typing()` | 结束打字状态 |
| `get_pending_message()` | 获取待发送的主动消息 |
| `update_last_message_time()` | 更新最后消息时间 |
| `trigger_summary_now()` | 已废弃，提示使用"浓缩"命令 |

---

### 5. src/summary_agent.py - 浓缩Agent（新）

**核心类**：`SummaryAgent`

**职责**：
- 每日聊天记录浓缩
- 核心事件提取
- 用户印象更新
- 完整的浓缩流程管理

**工作流程**：
```
1. 检查未浓缩的日期
   ↓
2. 逐天处理
   ├─ 生成对话摘要
   ├─ 提取核心事件
   └─ 添加到 chat_history_zip.json
   ↓
3. 基于所有新浓缩的记录，更新用户印象
   ↓
4. 保存用户印象
   ↓
5. 更新 system_config.json 中的 last_summary_date
```

**主要方法**：

| 方法名 | 功能 |
|-------|------|
| `summarize_single_day(date)` | 浓缩单天的聊天记录 |
| `update_user_impression(dates)` | 更新用户印象 |
| `run_summary()` | 执行完整的浓缩流程 |

**summarize_single_day 输入提示词**：
- 包含人格设定
- 要求生成 200 字以内的摘要
- 要求提取 3-5 个核心事件
- 返回 JSON 格式

**update_user_impression 输入提示词**：
- 包含当前已有印象
- 要求更新用户描述
- 要求提取性格特点（3-5个）
- 要求提取用户偏好（3-5条）
- 要求记录重要日期
- 要求记录用户目标
- 返回 JSON 格式

详细规则请参考 [SUMMARY_AGENT.md](SUMMARY_AGENT.md)

---

## 配置文件

### config.json - 路径配置（可选）
```json
{
    "data_dir": "data",
    "subdirectories": {
        "chat_history": "chat_history",
        "personality": "personality",
        "summarized_memory": "summarized_memory"
    },
    "filenames": {
        "chat_history": "chat_history.json",
        "personality": "personality.json",
        "summarized_memory": "summarized_memory.json"
    }
}
```

### .env - API配置
```env
DEEPSEEK_API_KEY=your_key
# 或 OPENAI_API_KEY
```

### personality.json - 人格设定
```json
{
    "name": "小希",
    "age": "22岁",
    "location": "上海",
    "gender": "女",
    "personality_traits": ["温柔", "害羞", "善解人意"],
    "greeting": "你好... 我是小希，很高兴认识你。",
    "relationship_level": 0,
    "experience": 0,
    "total_messages": 0
}
```

---

## 数据流图（新系统）

### 正常聊天流程
```
用户输入
    ↓
[main.py] 处理输入
    ↓
[MemoryManager] 保存消息到今日文件 +1经验
    ↓
[LLMClient] 分析情感 → 好感度 ±N
    ↓
[MemoryManager] 获取上下文
    ├─ 浓缩历史（summaries）
    ├─ 核心事件（core_events）
    ├─ 用户印象（impression）
    └─ 今日最近消息
    ↓
[LLMClient] 生成回复
    ↓
[Scheduler] 打字模拟（显示"正在输入"）
    ↓
[MemoryManager] 保存助手回复到今日文件
    ↓
显示回复 + 当前等级
```

### 浓缩流程（程序退出时）
```
触发浓缩
    ↓
[SummaryAgent] 获取未浓缩的日期（last_summary_date 之后）
    ↓
逐天处理：
    ├─ [MemoryManager] 加载某天的聊天记录
    ├─ [LLMClient] 生成摘要和核心事件
    └─ [MemoryManager] 添加到 chat_history_zip.json
    ↓
[SummaryAgent] 更新用户印象
    ├─ [LLMClient] 分析所有新浓缩的记录
    └─ [MemoryManager] 保存到 user_impression.json
    ↓
[MemoryManager] 更新 system_config.json 中的 last_summary_date
    ↓
完成！
```

---

## 核心特性详解

### 1. 新记忆系统
- **每日记录**：按日期单独保存聊天记录，无大小限制
- **浓缩历史**：chat_history_zip.json 存储摘要和核心事件
- **用户印象**：跟踪用户性格、偏好、重要日期、目标等
- **系统配置**：记录最后浓缩日期，避免重复处理

### 2. 经验值系统
- **基础获取**：每条用户消息 +1
- **内容奖励**：根据情感分析 ±1~5
- **升级阈值**：30/100/300/600/1000
- **降级**：经验值减少时可能降级

### 3. 打字延迟模拟
- 汉字：0.5秒/字
- 其他字符：0.1秒/字符
- 随机波动：±20%
- 最小延迟：1秒

### 4. 主动对话
- 活跃时间：8:00-24:00
- 间隔：等级越高越频繁（10-240分钟）
- 内容：结合时间、状态、历史话题、用户印象
- 追问：用户不回复时自动追问
- 最低沉默：至少1小时没说话才主动

### 5. 浓缩机制
- **触发时机**：程序退出时自动触发，或使用"浓缩"命令
- **浓缩内容**：每日摘要 + 核心事件
- **印象更新**：每次浓缩时同时更新用户印象
- **避免重复**：只处理 last_summary_date 之后的记录
- **今日例外**：今日的记录不会立即浓缩，等明天

### 6. 上下文构建（新）
LLM 收到的上下文包含：
1. 过往对话摘要（最近5条）
2. 核心事件（最多10条）
3. 用户印象（描述、性格、偏好）
4. 今日最近聊天记录（最多50条）

---

## 命令列表

| 命令 | 功能 |
|-----|------|
| `退出` / `exit` / `quit` / `q` | 退出程序（自动浓缩） |
| `浓缩` / `summary` / `总结` | 立即触发浓缩流程 |
| `状态` / `stats` | 显示当前状态和统计信息 |

---

## 工具脚本

### 1. migrate_data.py - 旧数据迁移
从旧的 v1.0 系统迁移到新的 v2.0 系统：
- 旧 chat_history.json → 今日的 chat_history_YYYY-MM-DD.json
- 旧 summarized_memory.json → 新的 chat_history_zip.json
- 自动备份旧文件

### 2. test_system.py - 系统功能测试
测试各个核心模块的功能是否正常。

### 3. check_imports.py - 导入检查
快速检查所有模块能否正常导入。

---

## 详细文档

- [SUMMARY_AGENT.md](SUMMARY_AGENT.md) - 浓缩 Agent 工作规则
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - 系统架构详解
- [功能检查报告.md](../功能检查报告.md) - 功能检查结果
- [主动消息场景说明.md](../主动消息场景说明.md) - 主动消息详解
- [NEW_SYSTEM_GUIDE.md](../NEW_SYSTEM_GUIDE.md) - 新系统使用指南
- [MEMORY_OPTIMIZATION.md](MEMORY_OPTIMIZATION.md) - 内存优化说明（历史）

---

## 版本历史

### v2.0（当前）
- 新记忆系统：每日聊天记录 + 集中浓缩
- SummaryAgent：专门的浓缩 Agent
- 用户印象管理
- 程序退出时自动浓缩
- 新增"浓缩"和"状态"命令
- 向后兼容设计

### v1.0（历史）
- 基础聊天功能
- 单个 chat_history.json
- 每日定时摘要
