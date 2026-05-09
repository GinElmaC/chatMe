import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any


class MemoryManager:
    """记忆管理类，处理聊天记录、人格设定和浓缩记忆的存储"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化记忆管理器，从配置文件读取路径设置"""
        self.config = self._load_config(config_path)
        self.base_dir = self.config.get("data_dir", "data")
        self.subdirs = self.config.get("subdirectories", {})
        self.filenames = self.config.get("filenames", {})
        
        self.chat_history_dir = os.path.join(self.base_dir, self.subdirs.get("chat_history", "chat_history"))
        self.personality_dir = os.path.join(self.base_dir, self.subdirs.get("personality", "personality"))
        self.summarized_memory_dir = os.path.join(self.base_dir, self.subdirs.get("summarized_memory", "summarized_memory"))
        
        self.chat_history_path = os.path.join(self.chat_history_dir, self.filenames.get("chat_history", "chat_history.json"))
        self.personality_path = os.path.join(self.personality_dir, self.filenames.get("personality", "personality.json"))
        self.summarized_memory_path = os.path.join(self.summarized_memory_dir, self.filenames.get("summarized_memory", "summarized_memory.json"))
        
        self._ensure_data_dirs()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件，返回配置字典"""
        default_config = {
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
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
                    return default_config
            except Exception:
                pass
        return default_config
    
    def _ensure_data_dirs(self):
        """确保所有数据目录存在，不存在则创建"""
        for directory in [self.base_dir, self.chat_history_dir, self.personality_dir, self.summarized_memory_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def load_chat_history(self) -> List[Dict[str, Any]]:
        """加载聊天历史记录，返回消息列表"""
        if os.path.exists(self.chat_history_path):
            try:
                with open(self.chat_history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def save_chat_history(self, history: List[Dict[str, Any]]):
        """保存聊天历史记录到文件"""
        with open(self.chat_history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def add_chat_message(self, role: str, content: str, timestamp: str = None):
        """添加一条聊天消息到历史记录"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        history = self.load_chat_history()
        history.append({
            "role": role,
            "content": content,
            "timestamp": timestamp
        })
        self.save_chat_history(history)
    
    def load_personality(self) -> Dict[str, Any]:
        """加载人格设定，返回人设字典"""
        if os.path.exists(self.personality_path):
            try:
                with open(self.personality_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._get_default_personality()
        return self._get_default_personality()
    
    def save_personality(self, personality: Dict[str, Any]):
        """保存人格设定到文件"""
        with open(self.personality_path, 'w', encoding='utf-8') as f:
            json.dump(personality, f, ensure_ascii=False, indent=2)
    
    def _get_default_personality(self) -> Dict[str, Any]:
        """返回默认的人格设定字典"""
        return {
            "name": "小希",
            "age": "22岁",
            "location": "上海",
            "gender": "女",
            "personality_traits": [
                "温柔",
                "害羞",
                "有点慢热",
                "善解人意",
                "会主动关心你"
            ],
            "user_description": "一个正在和我刚认识的网友，希望能慢慢了解彼此",
            "greeting": "你好... 我是小希，很高兴认识你。"
        }
    
    def load_summarized_memory(self) -> List[Dict[str, Any]]:
        """加载浓缩记忆，返回历史摘要列表"""
        if os.path.exists(self.summarized_memory_path):
            try:
                with open(self.summarized_memory_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def save_summarized_memory(self, summary: List[Dict[str, Any]]):
        """保存浓缩记忆到文件"""
        with open(self.summarized_memory_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    
    def add_summarized_memory(self, date: str, summary: str, chat_count: int):
        """添加一条对话摘要到浓缩记忆"""
        memories = self.load_summarized_memory()
        memories.append({
            "date": date,
            "summary": summary,
            "chat_count": chat_count,
            "timestamp": datetime.now().isoformat()
        })
        self.save_summarized_memory(memories)
    
    def clear_chat_history(self):
        """清空聊天历史记录"""
        self.save_chat_history([])
    
    def get_context_messages(self, limit: int = 50) -> List[Dict[str, str]]:
        """整合浓缩记忆和最近聊天记录，返回LLM上下文消息"""
        history = self.load_chat_history()
        summarized = self.load_summarized_memory()
        
        messages = []
        
        if summarized:
            summary_text = "【过往对话摘要】\n"
            for mem in summarized[-5:]:
                summary_text += f"{mem['date']}: {mem['summary']}\n"
            messages.append({"role": "system", "content": summary_text})
        
        recent_history = history[-limit:]
        for msg in recent_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        return messages
