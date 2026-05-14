import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
import re


class MemoryManager:
    """新的记忆管理器：每日聊天记录 + 集中浓缩历史 + 用户印象"""
    
    # 关系等级配置（保持向后兼容）
    LEVEL_THRESHOLDS = [30, 100, 300, 600, 1000]
    LEVEL_NAMES = ["陌生", "熟悉", "有好感", "亲密", "交往"]
    
    def __init__(self, config_path: str = "config.json"):
        """初始化记忆管理器"""
        self.config = self._load_config(config_path)
        self.base_dir = self.config.get("data_dir", "data")
        self.subdirs = self.config.get("subdirectories", {})
        self.filenames = self.config.get("filenames", {})
        
        self.chat_history_dir = os.path.join(self.base_dir, self.subdirs.get("chat_history", "chat_history"))
        self.personality_dir = os.path.join(self.base_dir, self.subdirs.get("personality", "personality"))
        
        # 确保基础目录存在
        self._ensure_data_dirs()
        
        # 今日日期和文件
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.today_chat_file = os.path.join(self.chat_history_dir, f"chat_history_{self.today}.json")
        
        # 浓缩历史文件
        self.zip_file = os.path.join(self.base_dir, "chat_history_zip.json")
        
        # 系统配置文件
        self.system_config_file = os.path.join(self.base_dir, "system_config.json")
        
        # 用户印象文件
        self.impression_file = os.path.join(self.base_dir, "user_impression.json")
        
        # 加载系统配置
        self.system_config = self._load_system_config()
        
        # 简单缓存
        self._personality_cache = None
        self._personality_cache_time = None
        self._cache_duration = 30
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件（保持向后兼容）"""
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
        """确保所有目录存在"""
        for directory in [self.base_dir, self.chat_history_dir, self.personality_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def _load_system_config(self) -> Dict[str, Any]:
        """加载系统配置"""
        if os.path.exists(self.system_config_file):
            try:
                with open(self.system_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "last_summary_date": None,
            "created_at": datetime.now().isoformat()
        }
    
    def _save_system_config(self):
        """保存系统配置"""
        with open(self.system_config_file, 'w', encoding='utf-8') as f:
            json.dump(self.system_config, f, ensure_ascii=False, indent=2)
    
    def get_uncompressed_dates(self) -> List[str]:
        """获取所有尚未浓缩的日期（今日之前）"""
        uncompressed = []
        
        if os.path.exists(self.chat_history_dir):
            for filename in os.listdir(self.chat_history_dir):
                if filename.startswith("chat_history_") and filename.endswith(".json"):
                    date_match = re.search(r"chat_history_(\d{4}-\d{2}-\d{2})\.json", filename)
                    if date_match:
                        date_str = date_match.group(1)
                        last_summary = self.system_config.get("last_summary_date")
                        
                        if last_summary is None or date_str > last_summary:
                            if date_str < self.today:
                                uncompressed.append(date_str)
        
        return sorted(uncompressed)
    
    def load_chat_history_by_date(self, date_str: str) -> List[Dict[str, Any]]:
        """加载指定日期的聊天记录"""
        filepath = os.path.join(self.chat_history_dir, f"chat_history_{date_str}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def load_today_chat_history(self) -> List[Dict[str, Any]]:
        """加载今日聊天记录"""
        return self.load_chat_history_by_date(self.today)
    
    def save_today_chat_history(self, history: List[Dict[str, Any]]):
        """保存今日聊天记录"""
        with open(self.today_chat_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def load_chat_history(self) -> List[Dict[str, Any]]:
        """加载聊天记录（保持向后兼容，加载今日记录）"""
        return self.load_today_chat_history()
    
    def add_chat_message(self, role: str, content: str, timestamp: str = None):
        """添加聊天消息"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        history = self.load_today_chat_history()
        history.append({
            "role": role,
            "content": content,
            "timestamp": timestamp
        })
        self.save_today_chat_history(history)
        
        if role == "user":
            self._add_experience(1)
    
    def load_zip_history(self) -> Dict[str, Any]:
        """加载浓缩历史"""
        if os.path.exists(self.zip_file):
            try:
                with open(self.zip_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"summaries": [], "core_events": []}
    
    def save_zip_history(self, zip_data: Dict[str, Any]):
        """保存浓缩历史"""
        with open(self.zip_file, 'w', encoding='utf-8') as f:
            json.dump(zip_data, f, ensure_ascii=False, indent=2)
    
    def add_to_zip_history(self, date_str: str, summary: str, core_events: List[str]):
        """添加到浓缩历史"""
        zip_data = self.load_zip_history()
        
        zip_data["summaries"].append({
            "date": date_str,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        })
        
        for event in core_events:
            if event not in zip_data["core_events"]:
                zip_data["core_events"].append(event)
        
        self.save_zip_history(zip_data)
        
        last_date = self.system_config.get("last_summary_date")
        if last_date is None or date_str > last_date:
            self.system_config["last_summary_date"] = date_str
            self._save_system_config()
    
    def load_user_impression(self) -> Dict[str, Any]:
        """加载用户印象"""
        if os.path.exists(self.impression_file):
            try:
                with open(self.impression_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "description": "",
            "traits": [],
            "preferences": [],
            "important_dates": [],
            "goals": [],
            "updated_at": None
        }
    
    def save_user_impression(self, impression: Dict[str, Any]):
        """保存用户印象"""
        impression["updated_at"] = datetime.now().isoformat()
        with open(self.impression_file, 'w', encoding='utf-8') as f:
            json.dump(impression, f, ensure_ascii=False, indent=2)
    
    def load_personality(self) -> Dict[str, Any]:
        """加载人格设定（保持向后兼容）"""
        personality_path = os.path.join(self.personality_dir, self.filenames.get("personality", "personality.json"))
        
        now = datetime.now()
        if (self._personality_cache is not None and 
            self._personality_cache_time is not None and
            (now - self._personality_cache_time).total_seconds() < self._cache_duration):
            return self._personality_cache
        
        if os.path.exists(personality_path):
            try:
                with open(personality_path, 'r', encoding='utf-8') as f:
                    personality = json.load(f)
                    if "relationship_level" not in personality:
                        personality["relationship_level"] = 0
                    if "experience" not in personality:
                        personality["experience"] = 0
                    if "total_messages" not in personality:
                        personality["total_messages"] = 0
                    self._personality_cache = personality
                    self._personality_cache_time = now
                    return personality
            except Exception:
                return self._get_default_personality()
        return self._get_default_personality()
    
    def save_personality(self, personality: Dict[str, Any]):
        """保存人格设定"""
        personality_path = os.path.join(self.personality_dir, self.filenames.get("personality", "personality.json"))
        with open(personality_path, 'w', encoding='utf-8') as f:
            json.dump(personality, f, ensure_ascii=False, indent=2)
        self._personality_cache = None
        self._personality_cache_time = None
    
    def _get_default_personality(self) -> Dict[str, Any]:
        """获取默认人格"""
        return {
            "name": "小希",
            "age": "22岁",
            "location": "上海",
            "gender": "女",
            "personality_traits": ["温柔", "害羞", "有点慢热", "善解人意", "会主动关心你"],
            "user_description": "一个正在和我刚认识的网友，希望能慢慢了解彼此",
            "greeting": "你好... 我是小希，很高兴认识你。",
            "relationship_level": 0,
            "experience": 0,
            "total_messages": 0
        }
    
    def get_context_messages(self, limit: int = 50) -> List[Dict[str, str]]:
        """获取对话上下文（整合浓缩历史、印象和今日记录）"""
        messages = []
        
        zip_data = self.load_zip_history()
        
        if zip_data.get("summaries"):
            summary_text = "【过往对话摘要】\n"
            for summary_item in zip_data["summaries"][-5:]:
                summary_text += f"{summary_item['date']}: {summary_item['summary']}\n"
            messages.append({"role": "system", "content": summary_text})
        
        if zip_data.get("core_events"):
            events_text = "【核心事件】\n" + "\n".join([f"- {evt}" for evt in zip_data["core_events"][-10:]])
            messages.append({"role": "system", "content": events_text})
        
        impression = self.load_user_impression()
        if impression.get("description") or impression.get("traits"):
            imp_text = "【对用户的印象】\n"
            if impression.get("description"):
                imp_text += f"描述: {impression['description']}\n"
            if impression.get("traits"):
                imp_text += f"性格: {', '.join(impression['traits'])}\n"
            if impression.get("preferences"):
                imp_text += f"偏好: {', '.join(impression['preferences'])}\n"
            messages.append({"role": "system", "content": imp_text})
        
        today_history = self.load_today_chat_history()
        recent_history = today_history[-limit:]
        for msg in recent_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        return messages
    
    def _add_experience(self, amount: int):
        """添加经验值"""
        personality = self.load_personality()
        current_exp = personality.get("experience", 0)
        current_level = personality.get("relationship_level", 0)
        
        new_exp = max(0, current_exp + amount)
        personality["experience"] = new_exp
        
        new_level = self._calculate_level(new_exp)
        if new_level > current_level:
            personality["relationship_level"] = new_level
            print(f"🎉 关系升级了！现在是【{self.LEVEL_NAMES[new_level]}】（Lv.{new_level+1}）")
        elif new_level < current_level:
            personality["relationship_level"] = new_level
            print(f"😔 关系降级了...现在是【{self.LEVEL_NAMES[new_level]}】（Lv.{new_level+1}）")
        
        personality["total_messages"] = personality.get("total_messages", 0) + 1
        self.save_personality(personality)
    
    def _calculate_level(self, experience: int) -> int:
        """计算等级"""
        for i, threshold in enumerate(self.LEVEL_THRESHOLDS):
            if experience < threshold:
                return i
        return len(self.LEVEL_THRESHOLDS)
    
    def get_relationship_level(self) -> int:
        return self.load_personality().get("relationship_level", 0)
    
    def get_experience(self) -> int:
        return self.load_personality().get("experience", 0)
    
    def add_content_bonus(self, score: int):
        clamped_score = max(-5, min(5, score))
        if clamped_score != score:
            print(f"内容评分超出范围，已限制为 {clamped_score}")
        self._add_experience(clamped_score)
    
    def add_follow_up_penalty(self):
        self._add_experience(-2)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        today_count = len(self.load_today_chat_history())
        zip_data = self.load_zip_history()
        
        return {
            "today": self.today,
            "today_chat_count": today_count,
            "total_summaries": len(zip_data.get("summaries", [])),
            "total_events": len(zip_data.get("core_events", [])),
            "last_summary_date": self.system_config.get("last_summary_date"),
            "uncompressed_dates": self.get_uncompressed_dates()
        }
    
    # === 向后兼容的方法 ===
    
    def load_summarized_memory(self) -> List[Dict[str, Any]]:
        """旧方法，返回浓缩记忆（向后兼容）"""
        zip_data = self.load_zip_history()
        return zip_data.get("summaries", [])
    
    def add_summarized_memory(self, date: str, summary: str, count: int):
        """旧方法（向后兼容），新系统中不使用"""
        pass
    
    def clear_chat_history(self):
        """旧方法（向后兼容），新系统中不使用"""
        pass
