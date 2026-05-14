# 千语新记忆系统使用说明

## 📋 系统概述

新的记忆系统实现了以下功能：
- **每日聊天记录**：按日期单独保存聊天记录，无大小限制
- **集中浓缩历史**：聊天记录在程序退出时自动浓缩到 `chat_history_zip.json`
- **用户印象管理**：记录用户性格、偏好、重要日期等信息
- **自动浓缩**：程序退出时自动触发浓缩，也支持手动触发

## 🚀 快速开始

### 1. 首次使用
```bash
# 如果有旧格式数据，先运行迁移
python migrate_data.py

# 然后正常启动
python main.py
```

### 2. 聊天中的命令
- **浓缩 / summary / 总结**：手动触发浓缩
- **状态 / stats**：查看当前系统状态
- **退出 / exit / quit / q**：退出程序（自动浓缩）

## 📁 数据结构

```
data/
├── chat_history/
│   ├── chat_history_2026-05-14.json  # 每日聊天记录
│   └── chat_history_2026-05-13.json
├── personality/
│   └── personality.json              # AI人格设定
├── chat_history_zip.json             # 浓缩历史
├── user_impression.json              # 用户印象
└── system_config.json                # 系统配置
```

## 🔍 核心文件说明

### chat_history_zip.json
```json
{
  "summaries": [
    {
      "date": "2026-05-14",
      "summary": "对话摘要...",
      "timestamp": "2026-05-14T12:00:00"
    }
  ],
  "core_events": [
    "重要事件1",
    "重要事件2"
  ]
}
```

### user_impression.json
```json
{
  "description": "用户描述...",
  "traits": ["性格1", "性格2"],
  "preferences": ["偏好1", "偏好2"],
  "important_dates": ["日期1", "日期2"],
  "goals": ["目标1", "目标2"],
  "updated_at": "..."
}
```

## 🧠 浓缩流程

1. **程序退出时**：自动检查未浓缩的历史日期
2. **每日浓缩**：为每一天生成对话摘要和核心事件
3. **更新印象**：基于浓缩内容更新对用户的印象
4. **保存结果**：将结果写入文件

## 📖 详情

更多详情请查看：
- [浓缩 Agent 规则](../agent/SUMMARY_AGENT.md)
- [系统架构](../agent/SYSTEM_ARCHITECTURE.md)
