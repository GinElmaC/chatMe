# AI女友

一个具有记忆功能的AI女友聊天程序，从陌生人慢慢变熟悉。

## 功能特性

1. **女友式聊天**：从陌生到熟悉，慢慢了解彼此，情感递进
2. **记忆系统**：
   - 聊天记录持久化
   - 女友人设设定文件
   - 浓缩聊天记录优化上下文
3. **定时任务**：
   - 定期重新加载人设设定和浓缩记录
   - 每日自动清洗聊天记录并生成摘要

## 项目结构

```
chatMe/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖包
├── config.json            # 配置文件（可自定义数据路径）
├── migrate_data.py        # 数据迁移脚本
├── data/                  # 数据目录（可在 config.json 中配置）
│   ├── chat_history/      # 聊天记录子目录
│   │   └── chat_history.json
│   ├── personality/       # 人格设定子目录
│   │   └── personality.json
│   └── summarized_memory/ # 浓缩记忆子目录
│       └── summarized_memory.json
├── skills/                # 技能目录（预留）
└── src/                   # 源代码
    ├── memory_manager.py  # 记忆管理模块
    ├── llm_client.py      # LLM 交互模块
    └── scheduler.py       # 定时任务模块
```

## 配置文件

编辑 `config.json` 可以自定义数据存储路径：

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

## 使用方法

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置 API Key：

   **方式一：使用 .env 文件（推荐）**
   - 复制 `.env.example` 为 `.env`
   - 在 `.env` 文件中填入你的 DeepSeek API Key
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入你的 API Key
   ```

   **方式二：设置环境变量**
   ```bash
   export DEEPSEEK_API_KEY="your-deepseek-api-key"
   # 可选：设置自定义 API 地址
   export DEEPSEEK_BASE_URL="https://your-api-endpoint.com"
   ```

3. 运行程序：
```bash
python main.py
```

## 数据迁移（如果有旧数据）

如果从旧版本升级，运行迁移脚本：

```bash
python3 migrate_data.py
```

## 配置人格设定

编辑 `data/personality/personality.json` 可以自定义助手的人格：

```json
{
    "name": "小助手",
    "description": "一个友好、健谈、有趣的AI助手",
    "personality_traits": [
        "友好",
        "健谈",
        "有耐心"
    ],
    "greeting": "你好呀！我是小助手..."
}
```

## 命令

- 输入 `退出` / `exit` / `quit` / `q`：退出程序
- 输入 `总结` / `summary`：立即生成当前聊天摘要

## 添加技能

在 `skills/` 目录下添加你的自定义技能模块。