import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.memory_manager import MemoryManager
from src.llm_client import LLMClient


class SummaryAgent:
    """专门负责浓缩聊天记录的 Agent"""
    
    def __init__(self, llm_client: LLMClient, memory_manager: MemoryManager):
        self.llm = llm_client
        self.memory = memory_manager
    
    def summarize_single_day(self, date_str: str) -> Optional[Dict[str, Any]]:
        """浓缩某一天的聊天记录"""
        chat_history = self.memory.load_chat_history_by_date(date_str)
        
        if not chat_history:
            return None
        
        personality = self.memory.load_personality()
        
        system_prompt = f"""你是一个专业的对话分析助手。请分析以下聊天记录，完成以下任务：
1. 生成一个简洁但全面的对话摘要（200字以内）
2. 提取本次对话中的核心事件（3-5条）

当前对话者设定：
- 名字: {personality.get('name')}
- 性格: {', '.join(personality.get('personality_traits', []))}

请以 JSON 格式返回，格式如下：
{{
  "summary": "对话摘要内容",
  "core_events": ["事件1", "事件2", "事件3"]
}}
"""
        
        user_content = f"日期: {date_str}\n聊天记录:\n"
        for msg in chat_history:
            role_text = "用户" if msg.get("role") == "user" else personality.get("name")
            user_content += f"{role_text}: {msg.get('content')}\n"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        try:
            result_text = self.llm.chat_with_typing_delay(messages, personality, stream=False)
            
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                result = json.loads(json_str)
                
                summary = result.get("summary", "")
                core_events = result.get("core_events", [])
                
                return {
                    "date": date_str,
                    "summary": summary,
                    "core_events": core_events
                }
        except Exception as e:
            print(f"浓缩 {date_str} 的记录时出错: {e}")
            return None
        
        return None
    
    def update_user_impression(self, dates: List[str]) -> Optional[Dict[str, Any]]:
        """更新用户印象"""
        all_history = []
        for date_str in dates:
            history = self.memory.load_chat_history_by_date(date_str)
            all_history.extend(history)
        
        if not all_history:
            return None
        
        current_impression = self.memory.load_user_impression()
        personality = self.memory.load_personality()
        
        system_prompt = f"""你是一个敏锐的观察者。根据对话历史，请更新对用户的印象。
请结合已有印象（如果有），完成以下内容：
1. 更新用户描述（200字以内）
2. 提取用户性格特点（3-5个关键词）
3. 提取用户偏好（兴趣、喜好等，3-5条）
4. 记录重要日期
5. 记录用户的目标或愿望

当前设定：
- AI名字: {personality.get('name')}
- 已有印象描述: {current_impression.get('description', '暂无')}
- 已有性格特点: {', '.join(current_impression.get('traits', []))}
- 已有偏好: {', '.join(current_impression.get('preferences', []))}
- 已有重要日期: {', '.join(current_impression.get('important_dates', []))}
- 已有目标: {', '.join(current_impression.get('goals', []))}

请以 JSON 格式返回：
{{
  "description": "用户描述",
  "traits": ["性格1", "性格2"],
  "preferences": ["偏好1", "偏好2"],
  "important_dates": ["日期1", "日期2"],
  "goals": ["目标1", "目标2"]
}}
"""
        
        user_content = "对话历史:\n"
        for msg in all_history:
            role_text = "用户" if msg.get("role") == "user" else personality.get("name")
            user_content += f"{role_text}: {msg.get('content')}\n"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        try:
            result_text = self.llm.chat_with_typing_delay(messages, personality, stream=False)
            
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                result = json.loads(json_str)
                
                new_impression = {
                    "description": result.get("description", current_impression.get("description", "")),
                    "traits": result.get("traits", current_impression.get("traits", [])),
                    "preferences": result.get("preferences", current_impression.get("preferences", [])),
                    "important_dates": result.get("important_dates", current_impression.get("important_dates", [])),
                    "goals": result.get("goals", current_impression.get("goals", [])),
                    "updated_at": datetime.now().isoformat()
                }
                
                return new_impression
        except Exception as e:
            print(f"更新用户印象时出错: {e}")
            return None
        
        return None
    
    def run_summary(self) -> Dict[str, Any]:
        """执行完整的浓缩流程"""
        uncompressed_dates = self.memory.get_uncompressed_dates()
        
        if not uncompressed_dates:
            return {"status": "nothing_to_summarize"}
        
        results = []
        for date_str in uncompressed_dates:
            print(f"正在浓缩 {date_str} 的聊天记录...")
            day_result = self.summarize_single_day(date_str)
            
            if day_result:
                self.memory.add_to_zip_history(
                    date_str,
                    day_result.get("summary", ""),
                    day_result.get("core_events", [])
                )
                results.append(day_result)
                print(f"✓ {date_str} 浓缩完成")
        
        if results:
            print("正在更新对用户的印象...")
            new_impression = self.update_user_impression(uncompressed_dates)
            if new_impression:
                self.memory.save_user_impression(new_impression)
                print("✓ 用户印象已更新")
        
        return {
            "status": "success",
            "summarized_dates": uncompressed_dates,
            "results": results
        }
