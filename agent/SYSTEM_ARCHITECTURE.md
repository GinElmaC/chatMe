# 千语（ChatMe）系统架构
========================

## 系统概述
千语是一个具有记忆和情感成长能力的 AI 伴侣聊天系统，采用模块化架构，支持单 Agent 和未来多 Agent 模式。

## 核心组件

### 1. 主程序 (main.py)
**职责**：
- 程序入口和主聊天循环
- 用户输入处理和响应显示
- 退出时的浓缩流程触发

**主要功能**：
- 初始化核心组件
- 处理聊天界面交互
- 管理退出时的浓缩流程
- 支持特殊命令（浓缩、状态查询等）

### 2. 记忆管理器 (src/memory_manager.py)
**职责**：
- 管理所有数据存储和读取
- 每日聊天记录管理
- 浓缩历史管理
- 用户印象管理

**数据结构**：
```
data/
├── chat_history/          # 每日聊天记录
│   ├── chat_history_2026-05-14.json
│   └── ...
├── personality/           # 人格设定
│   └── personality.json
├── chat_history_zip.json  # 浓缩历史
├── user_impression.json   # 用户印象
└── system_config.json     # 系统配置
```

### 3. LLM 客户端 (src/llm_client.py)
**职责**：
- 与 LLM API 交互
- 构建系统提示词
- 生成对话回复
- 分析用户语气
- 浓缩聊天记录

### 4. 定时任务调度器 (src/scheduler.py)
**职责**：
- 管理主动消息发送
- 处理每日摘要（保留向后兼容）
- 管理打字状态

### 5. 浓缩 Agent (src/summary_agent.py)
**职责**：
- 每日聊天记录浓缩
- 核心事件提取
- 用户印象更新
- 执行完整的浓缩流程

**详细规则**：请参考 [SUMMARY_AGENT.md](SUMMARY_AGENT.md)

## 工作流程

### 1. 启动流程
```
1. 初始化组件
2. 加载今日聊天记录
3. 检查是否有未浓缩的历史
4. 显示欢迎信息
5. 进入主聊天循环
```

### 2. 聊天流程
```
用户输入 -> 保存今日记录 -> 更新经验 -> 生成回复 -> 显示 -> 保存回复
```

### 3. 浓缩流程（程序退出时）
```
1. 触发 atexit 钩子
2. 检查未浓缩的日期
3. 逐天浓缩记录
4. 提取核心事件
5. 更新用户印象
6. 保存浓缩结果
7. 更新最后浓缩日期
```

## 数据流动

### 聊天时
```
用户消息 -> chat_history_YYYY-MM-DD.json
AI 回复 -> chat_history_YYYY-MM-DD.json
```

### 浓缩时
```
chat_history_*.json -> 浓缩 Agent -> chat_history_zip.json
                      -> user_impression.json
                      -> 更新 system_config.json
```

### 对话上下文构建
```
chat_history_zip.json (摘要) -> 系统提示词
user_impression.json (印象) -> 系统提示词
chat_history_today.json (今日) -> 对话上下文
```

## 扩展架构（未来）

### 多 Agent 系统
```
Agent 1 (小希) ─┐
Agent 2 (雪菜) ─┼── Agent Manager
Agent 3 (小明) ─┘
```

### 功能模块
```
核心聊天 ─┐
技能系统 ─┼── 主程序
记忆系统 ─┘
```

## 核心特性

1. **渐进式记忆**
   - 短期：今日完整聊天
   - 中期：近期摘要
   - 长期：核心事件和用户印象

2. **情感成长**
   - 经验值系统
   - 关系等级递进
   - 用户印象积累

3. **安全设计**
   - 完整历史保留（每日记录）
   - 自动备份
   - 数据迁移支持

## 配置要点

- API 配置：`.env`
- 路径配置：代码中管理
- 人格设定：`data/personality/personality.json`

---
**版本**：2.0 (新记忆系统)  
**最后更新**：2026-05-14
