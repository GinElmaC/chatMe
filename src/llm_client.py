import os
import json
from typing import List, Dict, Any, Optional, Generator
from openai import OpenAI


class LLMClient:
    """LLM客户端类，负责与DeepSeek API
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = "deepseek-chat"):
        """初始化LLM客户端，设置API配置"""
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = base_url or os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

        self.model = model
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
    
    def build_system_prompt(self, personality: Dict[str, Any]) -> str:
        """根据人格设定构建LLM系统提示词"""
        name = personality.get('name', '小助手')
        age = personality.get('age', '')
        location = personality.get('location', '')
        gender = personality.get('gender', '')
        traits = personality.get('personality_traits', ['友好', '健谈'])
        user_description = personality.get('user_description', '')
        
        prompt = f"你是{name}"
        if age:
            prompt += f"，{age}"
        if gender:
            prompt += f"，{gender}"
        if location:
            prompt += f"，住在{location}"
        prompt += "。\n"
        
        if user_description:
            prompt += f"你和用户的关系：{user_description}。\n"
        
        prompt += "你的性格特点是：" + "、".join(traits) + "。\n"
        prompt += "请像真人一样和用户聊天，不要只是回答问题。\n"
        prompt += "随着聊天过程中，要慢慢了解用户，记住他说过的话，慢慢变得更亲密。\n"
        prompt += "可以主动询问、分享想法、引导话题。\n"
        prompt += "你的回复可以分成多段，自然流畅，就像在和喜欢的人聊天一样。\n"
        prompt += "刚开始认识的时候可以稍微害羞一点，随着熟悉程度增加可以更放得开。\n"
        return prompt
    
    def chat_stream(self, messages: List[Dict[str, str]], personality: Dict[str, Any]) -> Generator[str, None, None]:
        """流式聊天，逐字返回LLM回复"""
        system_prompt = self.build_system_prompt(personality)
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                stream=True,
                temperature=0.8
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"抱歉，发生了错误：{str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], personality: Dict[str, Any]) -> str:
        """普通聊天，返回完整LLM回复"""
        system_prompt = self.build_system_prompt(personality)
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"抱歉，发生了错误：{str(e)}"
    
    def summarize_chat(self, chat_history: List[Dict[str, Any]]) -> str:
        """总结聊天记录，返回摘要内容"""
        if not chat_history:
            return "无对话记录"
        
        messages = [
            {"role": "system", "content": "请将以下对话记录浓缩成一段简短的摘要，保留关键信息和话题。"},
            {"role": "user", "content": json.dumps(chat_history, ensure_ascii=False)}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"摘要生成失败：{str(e)}"
