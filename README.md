# 我把她叫做千语

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
├── main.py                 # 命令行版本主程序
├── main_qq.py            # QQ版主程序
├── requirements.txt       # 依赖包
├── config/                # 配置文件示例
│   ├── .env.example
│   ├── config.json.example
│   └── go-cqhttp_config.yml.example
├── docs/                  # 文档目录
│   ├── NEW_SYSTEM_GUIDE.md    # 新系统使用指南
│   ├── qq_integration.md      # QQ集成指南
│   ├── 主动消息场景说明.md
│   └── 功能检查报告.md
├── scripts/               # 工具脚本
│   ├── migrate_data.py       # 数据迁移脚本
│   └── fix_old_chat_history.py
├── tests/                 # 测试文件
│   ├── check_imports.py
│   ├── cleanup_test.py
│   └── test_system.py
├── agent/                 # Agent架构文档
│   ├── agent.md
│   ├── SUMMARY_AGENT.md
│   ├── MEMORY_OPTIMIZATION.md
│   └── SYSTEM_ARCHITECTURE.md
├── skills/                # 技能目录（预留）
├── src/                   # 源代码
│   ├── memory_manager.py  # 记忆管理模块
│   ├── llm_client.py      # LLM 交互模块
│   ├── scheduler.py       # 定时任务模块
│   ├── summary_agent.py   # 聊天记录浓缩Agent
│   ├── qq_adapter.py      # QQ机器人适配器
│   └── utils.py           # 工具函数
└── data/                  # 数据目录（运行时生成）
    ├── chat_history/      # 聊天记录子目录
    ├── personality/       # 人格设定子目录
    ├── summarized_memory/ # 浓缩记忆子目录
    ├── user_impression/   # 用户印象子目录
    └── system_config.json
```

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

**方式一：使用 .env 文件（推荐）**
- 复制 `config/.env.example` 为 `.env`
- 在 `.env` 文件中填入你的 DeepSeek API Key
```bash
cp config/.env.example .env
# 编辑 .env 文件，填入你的 API Key
```

**方式二：设置环境变量**
```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
# 可选：设置自定义 API 地址
export DEEPSEEK_BASE_URL="https://your-api-endpoint.com"
```

### 3. 运行程序

#### 命令行版本
```bash
python main.py
```

#### QQ版
1. 先下载并配置 go-cqhttp（参考 `docs/qq_integration.md`）
2. 运行千语QQ版：
```bash
python main_qq.py
```

## 数据迁移（如果有旧数据）

如果从旧版本升级，运行迁移脚本：

```bash
python3 scripts/migrate_data.py
```

## 详细文档

- 新系统使用指南：[docs/NEW_SYSTEM_GUIDE.md](docs/NEW_SYSTEM_GUIDE.md)
- QQ集成指南：[docs/qq_integration.md](docs/qq_integration.md)
- Agent架构文档：[agent/agent.md](agent/agent.md)
- 浓缩Agent说明：[agent/SUMMARY_AGENT.md](agent/SUMMARY_AGENT.md)

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
