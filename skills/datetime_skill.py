
from datetime import datetime
from typing import Dict, Any, Optional
from .base import BaseSkill


class DateTimeSkill(BaseSkill):
    """日期/时间查询技能"""
    
    name = "datetime"
    description = "查询当前日期、时间、星期几等"
    version = "2.0.0"
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
        """判断是否能处理该消息（更严格的关键词匹配）"""
        # 更严格的关键词组合
        keywords = [
            # 完整的询问短语
            "今天是几号", "今天星期几", "现在几点", "几点了", "几号了",
            "今天几号", "今天是星期几", "现在是几点", "现在是几号",
            "今天的日期", "现在的时间", "今天是周几",
            
            # 简短但需要配合问号或语气词
            "现在是", "今天是", "什么时间", "什么日期", "什么日子",
        ]
        
        # 英文关键词
        english_keywords = [
            "what time", "what date", "what day", "what is today",
            "current time", "current date", "today is",
        ]
        
        # 检查关键词组合（更严格）
        message_lower = message.lower()
        
        # 检查是否有明显的询问意图
        has_question_mark = "?" in message or "？" in message
        has_ask_word = any(word in message for word in ["问", "查", "问一下", "告诉我"])
        
        # 检查中文关键词
        for keyword in keywords:
            if keyword in message:
                # 如果是完整的短语，直接匹配
                if keyword in ["今天是几号", "今天星期几", "现在几点", "几点了"]:
                    return True
                # 否则需要有问号或询问词
                if has_question_mark or has_ask_word:
                    return True
        
        # 检查英文关键词
        for keyword in english_keywords:
            if keyword in message_lower:
                return True
        
        return False
    
    def execute(self, message: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """执行技能，返回结构化时间数据"""
        now = datetime.now()
        
        # 获取各种日期/时间信息
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        weekday = now.weekday()
        weekday_str = self.WEEKDAY_MAP[weekday]
        
        # 获取时间段问候
        if 5 <= hour < 9:
            time_period = "早上"
        elif 9 <= hour < 12:
            time_period = "上午"
        elif 12 <= hour < 14:
            time_period = "中午"
        elif 14 <= hour < 18:
            time_period = "下午"
        elif 18 <= hour < 22:
            time_period = "晚上"
        else:
            time_period = "深夜"
        
        # 返回结构化数据
        return {
            "type": "datetime",
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "weekday": weekday_str,
            "time_period": time_period,
            "formatted_date": f"{year}年{month}月{day}日",
            "formatted_time": f"{hour}点{minute}分",
            "full_datetime": f"{year}年{month}月{day}日 {weekday_str} {hour}点{minute}分"
        }

