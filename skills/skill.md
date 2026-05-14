# ChatMe Skills 开发文档

## 目录概述

`skills/` 目录是 ChatMe 项目的技能扩展模块目录，用于存放自定义的功能技能。目前该目录处于预留状态，等待开发者添加技能。

---

## 技能系统设计理念

ChatMe 的技能系统旨在为 AI 助手添加可插拔的功能模块，使得：
- 功能模块化，易于维护
- 支持动态加载和卸载
- 与核心聊天流程无缝集成
- 可以根据关系等级解锁新技能

---

## 技能开发规范

### 1. 技能文件结构

每个技能应该是一个独立的 Python 模块，建议的文件结构：

```
skills/
├── __init__.py              # 包初始化文件
├── skill.md                 # 本文档
├── my_skill/                # 技能包（推荐方式）
│   ├── __init__.py
│   ├── core.py              # 核心逻辑
│   └── config.py            # 配置
└── simple_skill.py          # 单文件技能（简单技能）
```

### 2. 技能类设计规范

推荐的技能基类结构：

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseSkill(ABC):
    """技能基类"""
    
    name: str = "base_skill"
    description: str = "基础技能"
    version: str = "1.0.0"
    
    # 解锁该技能所需的关系等级 (0-4)
    unlock_level: int = 0
    
    def __init__(self, memory_manager, llm_client):
        """
        初始化技能
        
        Args:
            memory_manager: MemoryManager 实例
            llm_client: LLMClient 实例
        """
        self.memory = memory_manager
        self.llm = llm_client
    
    @abstractmethod
    def can_handle(self, message: str) -> bool:
        """
        判断该技能是否能处理用户消息
        
        Args:
            message: 用户输入的消息
            
        Returns:
            bool: 是否能处理
        """
        pass
    
    @abstractmethod
    def handle(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """
        处理用户消息
        
        Args:
            message: 用户输入的消息
            context: 上下文信息
            
        Returns:
            Optional[str]: 回复内容，None 表示不回复
        """
        pass
    
    def is_available(self) -> bool:
        """
        检查技能是否可用（根据关系等级等）
        
        Returns:
            bool: 是否可用
        """
        current_level = self.memory.get_relationship_level()
        return current_level >= self.unlock_level
```

### 3. 技能注册方式

在 `skills/__init__.py` 中注册技能：

```python
from .my_skill import MySkill

# 注册所有可用技能
SKILLS = [
    MySkill,
    # 添加更多技能...
]

__all__ = ['SKILLS']
```

---

## 技能示例

### 示例 1：天气查询技能

```python
# skills/weather_skill.py
import requests
from typing import Dict, Any, Optional


class WeatherSkill:
    name = "weather"
    description = "查询天气"
    version = "1.0.0"
    unlock_level = 1  # 熟悉等级解锁
    
    def __init__(self, memory_manager, llm_client):
        self.memory = memory_manager
        self.llm = llm_client
        # 这里可以配置天气API密钥
    
    def can_handle(self, message: str) -> bool:
        keywords = ["天气", "下雨", "温度", "晴天", "阴天"]
        return any(keyword in message for keyword in keywords)
    
    def handle(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        # 简化示例，实际应调用真实天气API
        personality = self.memory.load_personality()
        name = personality.get('name', '千语')
        
        return f"{name}查了一下，今天天气晴朗，温度适宜，很适合出门呢~"
    
    def is_available(self) -> bool:
        current_level = self.memory.get_relationship_level()
        return current_level >= self.unlock_level
```

### 示例 2：日程提醒技能

```python
# skills/reminder_skill.py
from datetime import datetime
from typing import Dict, Any, Optional


class ReminderSkill:
    name = "reminder"
    description = "设置日程提醒"
    version = "1.0.0"
    unlock_level = 2  # 有好感解锁
    
    def __init__(self, memory_manager, llm_client):
        self.memory = memory_manager
        self.llm = llm_client
    
    def can_handle(self, message: str) -> bool:
        keywords = ["提醒", "备忘", "记住", "别忘了"]
        return any(keyword in message for keyword in keywords)
    
    def handle(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        # 这里可以实现提醒逻辑
        personality = self.memory.load_personality()
        name = personality.get('name', '千语')
        
        return f"好的~ {name}记住啦，到时候会提醒你的！😊"
    
    def is_available(self) -> bool:
        current_level = self.memory.get_relationship_level()
        return current_level >= self.unlock_level
```

---

## 技能集成到主程序

### 在 main.py 中集成技能系统

```python
# 在 main.py 中添加
from skills import SKILLS


def main():
    # ... 现有初始化代码 ...
    
    # 初始化技能
    active_skills = []
    for SkillClass in SKILLS:
        skill = SkillClass(memory_manager, llm_client)
        if skill.is_available():
            active_skills.append(skill)
            print(f"✅ 已加载技能: {skill.name}")
    
    # ... 主聊天循环 ...
    
    # 在处理用户输入时
    user_input = input("你: ").strip()
    
    # 先检查是否有技能可以处理
    handled = False
    for skill in active_skills:
        if skill.can_handle(user_input):
            response = skill.handle(user_input, {})
            if response:
                print(f"{name}: {response}")
                memory_manager.add_chat_message("assistant", response)
                handled = True
                break
    
    if not handled:
        # 使用默认的 LLM 聊天
        # ... 现有聊天代码 ...
```

---

## 技能分类建议

### 1. 生活服务类
- 天气查询
- 日历/日程
- 闹钟提醒
- 计时器

### 2. 信息查询类
- 百科知识
- 翻译
- 计算器
- 单位换算

### 3. 娱乐互动类
- 讲笑话
- 猜谜语
- 诗词对答
- 小游戏

### 4. 关系进阶类（高等级解锁）
- 亲密问候
- 纪念日提醒
- 专属昵称
- 个性化互动

---

## 技能最佳实践

1. **渐进式解锁**：根据关系等级解锁更高级的技能
2. **无缝集成**：技能回复应该符合角色设定和当前关系等级
3. **错误处理**：技能应该优雅处理失败情况，回退到普通聊天
4. **配置灵活**：技能配置应该可通过 config.json 或 personality.json 配置
5. **性能考虑**：耗时操作应该异步执行，避免阻塞主聊天流程

---

## 待办事项

- [ ] 实现技能自动加载机制
- [ ] 实现技能优先级管理
- [ ] 添加技能配置文件支持
- [ ] 实现技能启用/禁用功能
- [ ] 添加技能开发模板
- [ ] 提供更多官方示例技能
