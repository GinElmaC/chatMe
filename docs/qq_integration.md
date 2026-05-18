
# 千语QQ集成指南

## 功能概述

千语现在支持通过QQ与AI聊天！使用 go-cqhttp 作为QQ机器人框架，实现千语与QQ的完美结合。

**主要功能：**
- 私聊和群聊支持
- 保留所有原有功能（记忆系统、主动聊天、打字模拟、好感度系统等）
- QQ消息实时监听和回复
- 命令系统支持

---

## 准备工作

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载 go-cqhttp

go-cqhttp 是一个开源的 QQ 机器人框架，我们需要先下载它：

- **下载地址**：https://github.com/Mrs4s/go-cqhttp/releases
- 选择适合你系统的版本下载

### 3. 配置 go-cqhttp

1. 把下载的 go-cqhttp 放到项目目录或任意位置
2. 运行 go-cqhttp 首次生成配置文件
3. 使用我们提供的配置文件 `go-cqhttp_config.yml.example`
4. 复制配置文件并命名为 `config.yml`
5. 修改配置中的 QQ 账号

**配置文件修改说明：**
- `account.uin`: 填写你的 QQ 号
- `account.password`: 填写密码，留空则扫码登录

---

## 使用方法

### 第一步：启动 go-cqhttp

```bash
# Windows
go-cqhttp.exe

# Linux/Mac
./go-cqhttp
```

首次运行会要求选择登录方式，建议选择扫码登录。

### 第二步：启动千语QQ版

#### 方式一：直接运行（推荐）
```bash
python main_qq.py
```
程序会提示你输入聊天的QQ号或群号。

#### 方式二：命令行参数
```bash
# 私聊
python main_qq.py 123456789 private

# 群聊
python main_qq.py 123456 group
```

---

## 命令系统

在QQ中发送以下命令来控制千语：

| 命令 | 功能 |
|-----|------|
| 普通文字 | 千语正常回复聊天 |
| `/状态` 或 `/stats` | 查看当前关系状态和统计数据 |
| `/浓缩` 或 `/summary` | 手动触发聊天记录浓缩 |

---

## 安全与注意事项

### QQ 机器人使用风险说明

1. **QQ 账号风险**
   - 使用 go-cqhttp 存在一定的封号风险
   - 建议使用小号进行测试
   - 避免频繁发送消息，模拟真人聊天节奏

2. **聊天记录**
   - 聊天数据会保存在本地 `data/` 目录下
   - 请定期备份聊天数据

3. **使用建议**
   - 不要在群聊中过度活跃
   - 回复间隔适当拉长
   - 避免发送敏感内容

---

## 架构设计

### 文件结构

```
chatMe/
├── main.py              # 命令行版本
├── main_qq.py          # QQ版本（新）
├── go-cqhttp_config.yml.example  # go-cqhttp 配置文件示例
└── src/
    ├── qq_adapter.py    # QQ适配器（新）
    └── ...
```

### 模块说明

#### QQAdapter (src/qq_adapter.py)
QQ适配器，负责与 go-cqhttp 通信。

主要功能：
- HTTP API 连接（发送消息）
- WebSocket 连接（接收消息）
- 聊天目标管理
- 消息收发处理

#### QQChatManager (src/qq_adapter.py)
QQ聊天管理器，整合QQ适配器和千语系统。

主要功能：
- 协调各个模块
- 消息处理流程
- 命令处理
- 主动聊天支持

---

## 常见问题

### 1. go-cqhttp 无法启动

**问题**：启动后闪退或无法连接
**解决方案**：
- 确保配置文件格式正确
- 检查网络连接
- 尝试使用扫码登录代替密码登录

### 2. 千语无法连接到 go-cqhttp

**问题**：提示无法连接到 go-cqhttp
**解决方案**：
- 确认 go-cqhttp 已启动
- 检查端口是否被占用
- 确认配置文件中的地址是 127.0.0.1:8080

### 3. 无法收到消息

**问题**：发送消息后千语没有反应
**解决方案**：
- 确认目标QQ号设置正确
- 检查 go-cqhttp 是否正常连接
- 查看控制台日志

### 4. 如何切换到群聊

**答案**：
```bash
python main_qq.py 123456789 group
```
将 `123456789` 替换为你的群号

---

## 与命令行版本对比

| 功能 | 命令行版本 (main.py) | QQ版本 (main_qq.py) |
|-----|---------------------|---------------------|
| 登录方式 | 无 | go-cqhttp QQ登录 |
| 聊天方式 | 控制台输入 | QQ聊天 |
| 打字模拟 | 控制台显示 | 模拟打字延迟 |
| 记忆系统 | ✅ 完全一致 | ✅ 完全一致 |
| 主动聊天 | ✅ 支持 | ✅ 支持 |
| 浓缩功能 | ✅ 支持 | ✅ 支持 |
| 关系系统 | ✅ 完全一致 | ✅ 完全一致 |
| 私聊 | - | ✅ 支持 |
| 群聊 | - | ✅ 支持 |

---

## 技术细节

### go-cqhttp 通信原理

千语通过两种方式与 go-cqhttp 通信：

1. **HTTP API** - 发送消息
   - 使用 `send_private_msg` 发送私聊
   - 使用 `send_group_msg` 发送群聊

2. **WebSocket** - 接收消息
   - 监听消息上报
   - 实时处理用户消息

### 消息处理流程

```
用户发送QQ消息
    ↓
go-cqhttp WebSocket上报
    ↓
QQAdapter 接收和过滤
    ↓
QQChatManager 处理
    ↓
调用原千语系统生成回复
    ↓
通过HTTP API 发送回QQ
```

---

## 高级配置

### 自定义端口

如果你想修改 go-cqhttp 的端口，可以在运行时指定：

```bash
python main_qq.py 123456 private http://127.0.0.1:9090 ws://127.0.0.1:9090/ws
```

### 同时使用命令行和QQ版

两个版本可以共用同一套数据和记忆系统，互不冲突！

---

## 进一步参考

- go-cqhttp 官方文档：https://docs.go-cqhttp.org/
- go-cqhttp API 文档：https://docs.go-cqhttp.org/api/

---

祝使用愉快！如有问题请查看控制台日志。
