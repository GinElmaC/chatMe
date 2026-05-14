# 内存优化总结

## 已修复的内存泄漏风险

### 1. 线程对象无限累积
**位置**: `src/scheduler.py`
**问题**: `Scheduler.threads` 列表会不断累积线程对象
**修复**:
- 添加了 `_cleanup_finished_threads()` 方法定期清理已结束的线程
- `stop()` 方法现在也会清理线程列表
- `start()` 方法在启动前先清理已结束的线程

### 2. 聊天记录无限增长
**位置**: `src/memory_manager.py`
**问题**: 聊天记录没有条数限制，可能无限增长
**修复**:
- 配置 `MAX_CHAT_HISTORY = 100` 条限制
- 添加 `_should_trigger_summary()` 检查方法
- 达到限制后自动触发浓缩

### 3. 文件大小无限增长
**位置**: `src/memory_manager.py`
**问题**: 聊天记录文件可能变得很大
**修复**:
- 配置 `MAX_CHAT_HISTORY_SIZE = 10MB` 限制
- 添加 `_get_file_size()` 方法检查文件大小

### 4. 浓缩记忆无限增长
**位置**: `src/memory_manager.py`
**问题**: 历史摘要会不断累积
**修复**:
- 配置 `MAX_SUMMARIZED_MEMORIES = 365` (保留1年)
- `load_summarized_memory()` 和 `save_summarized_memory()` 都会自动限制数量

### 5. 重复的文件 IO
**位置**: `src/memory_manager.py`
**问题**: 频繁调用 `load_personality()` 和 `load_chat_history()` 造成不必要的 IO
**修复**:
- 添加内存缓存机制 (30秒过期)
- 减少磁盘读取次数

## 新增功能

### 1. 主动浓缩触发
`add_chat_message()` 现在会返回 `Optional[List[Dict[str, Any]]]`
- 达到限制时返回需要浓缩的历史记录
- 主程序会检测并自动执行浓缩流程

### 2. 内存监控工具
新增 `src/utils.py`:
- `get_memory_usage()` - 获取内存使用情况
- `force_gc()` - 强制执行垃圾回收
- `get_disk_usage()` - 获取磁盘使用情况
- `MemoryMonitor` - 内存监控类

## 配置参数

```python
# 聊天记录限制
MAX_CHAT_HISTORY = 100  # 最大条数
MAX_CHAT_HISTORY_SIZE = 10 * 1024 * 1024  # 10MB

# 浓缩记忆限制
MAX_SUMMARIZED_MEMORIES = 365  # 保留1年的摘要

# 缓存配置
_cache_duration = 30  # 缓存有效期30秒
```

## 使用说明

### 现有功能保持不变
- 单 Agent 模式继续使用 `main.py`
- 所有现有 API 兼容

### 新功能
- 聊天记录达到 100 条或 10MB 时会自动浓缩
- 自动保留最近 365 天的摘要
- 优化的缓存减少磁盘 IO

## 建议

1. **定期备份**: 定期备份 `data/` 或 `agents_data/` 目录
2. **监控磁盘**: 注意磁盘空间使用情况
3. **可选**: 如需更多监控，可以在主程序中集成 `MemoryMonitor`
