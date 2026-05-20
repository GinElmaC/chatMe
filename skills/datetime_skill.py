
from datetime import datetime
from typing import Dict, Any, Optional
from .base import BaseSkill


class DateTimeSkill(BaseSkill):
    """日期/时间查询技能"""
    
    name = "datetime"
    description = "查询当前日期、时间、星期几等"
    version = "1.0.0"
    unlock_level = 0  # 所有人都可以使用
    
    # 中文星期几映射
    WEEKDAY_MAP = {
        0: "星期一",
        1: "星期二",
        2: "星期三",
        3: "星期四",
        4: "星期五",
        5: "星期六",
        6: "星期日"
    }
    
    def can_handle(self, message: str) -> bool:
        """判断是否能处理该消息"""
        keywords = [
            "今天", "几号", "日期", "星期", "几点", "时间",
            "现在", "此刻", "当前时间", "什么日子",
            "today", "date", "time", "now", "what day",
            "几点了", "几号了"
        ]
        return any(keyword in message for keyword in keywords)
    
    def handle(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """处理用户消息"""
        now = datetime.now()
        
        # 获取各种日期/时间信息
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        weekday = now.weekday()
        weekday_str = self.WEEKDAY_MAP[weekday]
        
        # 获取性格设定
        personality = self.memory.load_personality()
        name = personality.get('name', '千语')
        
        # 根据消息内容生成不同的回复
        if any(key in message for key in ["几点", "时间", "time", "now"]):
            # 询问时间
            reply = self._get_time_reply(now, name, hour, minute, weekday_str)
        elif any(key in message for key in ["星期", "周几", "what day"]):
            # 询问星期
            reply = f"今天是{weekday_str}呀~"
        elif any(key in message for key in ["今天", "几号", "日期", "date"]):
            # 询问日期
            reply = f"今天是{year}年{month}月{day}日，{weekday_str}~"
        else:
            # 通用回复
            reply = self._get_general_reply(now, name, year, month, day, hour, minute, weekday_str)
        
        return reply
    
    def _get_time_reply(self, now, name, hour, minute, weekday_str):
        """获取时间相关的回复"""
        # 根据时间段选择语气
        if 5 <= hour < 9:
            greet = "早上好呀"
        elif 9 <= hour < 12:
            greet = "上午好"
        elif 12 <= hour < 14:
            greet = "中午好"
        elif 14 <= hour < 18:
            greet = "下午好"
        elif 18 <= hour < 22:
            greet = "晚上好"
        else:
            greet = "现在是"
        
        time_str = f"{hour}点{minute}分"
        
        replies = [
            f"{greet}~现在是{time_str}，{weekday_str}~",
            f"{name}看看...哦，现在是{time_str}啦！",
            f"现在是{time_str}哦~有什么想做的吗？",
            f"现在已经是{time_str}啦，时间过得好快呀~"
        ]
        
        # 简单随机选择一个回复
        import random
        return random.choice(replies)
    
    def _get_general_reply(self, now, name, year, month, day, hour, minute, weekday_str):
        """获取通用回复"""
        time_str = f"{hour}点{minute}分"
        replies = [
            f"今天是{year}年{month}月{day}日，{weekday_str}，现在是{time_str}~",
            f"{name}告诉你哦，现在是{year}年{month}月{day}日{weekday_str}，{time_str}啦~",
            f"让{name}看看...今天是{month}月{day}日{weekday_str}，现在是{time_str}~"
        ]
        
        import random
        return random.choice(replies)
