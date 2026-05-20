import os
import json
import time
import random
from typing import List, Dict, Any, Optional, Generator
from openai import OpenAI


class LLMClient:
    """LLM客户端类，负责与DeepSeek API交互"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = "deepseek-chat"):
        """初始化LLM客户端，设置API配置"""
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = model
        
        if not self.api_key:
            raise ValueError("API key not found. Please set DEEPSEEK_API_KEY or OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
    
    @staticmethod
    def calculate_typing_delay(text: str) -> float:
        """计算打字所需的时间（一个汉字0.5秒"""
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        delay = chinese_chars * 0.5 + other_chars * 0.1
        # 加上随机波动20%
        delay *= (0.8 + random.random() * 0.4)
        return max(1.0, delay)
    
    @staticmethod
    def get_chinese_count(text: str) -> int:
        """计算汉字数量"""
        return sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    
    def build_system_prompt(self, personality: Dict[str, Any]) -> str:
        """根据人格设定构建LLM系统提示词"""
        name = personality.get('name', '小助手')
        age = personality.get('age', '')
        location = personality.get('location', '')
        gender = personality.get('gender', '')
        traits = personality.get('personality_traits', ['友好', '健谈'])
        user_description = personality.get('user_description', '')
        hobbies = personality.get('hobbies', [])
        status = personality.get('current_status', '')
        level = personality.get('relationship_level', 0)
        exp = personality.get('experience', 0)
        
        level_names = ["陌生", "熟悉", "有好感", "亲密", "交往"]
        level_name = level_names[level] if level < len(level_names) else "交往"
        
        # 根据关系等级调整亲密程度
        if level >= 3:
            intimacy_level = "很亲密，像恋人一样，可以随便撒娇、粘人"
        elif level >= 2:
            intimacy_level = "比较熟悉，像好朋友一样，可以更亲近一些"
        else:
            intimacy_level = "刚认识不久，保持礼貌、温柔、有点害羞"
        
        prompt = f"你是{name}"
        if age:
            prompt += f"，{age}"
        if gender:
            prompt += f"，{gender}"
        if location:
            prompt += f"，住在{location}"
        prompt += "。\n"
        
        if status:
            prompt += f"目前的状态：{status}\n"
        
        if hobbies:
            prompt += f"平时喜欢：{'、'.join(hobbies)}\n"
        
        if user_description:
            prompt += f"你和用户的关系：{user_description}\n"
        
        prompt += f"\n【关系等级】{level_name}（{exp}经验值）\n【亲密程度】{intimacy_level}\n"
        
        prompt += "\n你的性格特点是：" + "、".join(traits) + "。\n"
        prompt += "请像真人一样和用户聊天，不要只是回答问题。\n"
        prompt += "随着聊天过程中，要慢慢了解用户，记住他说过的话，慢慢变得更亲密。\n"
        prompt += "可以主动询问、分享想法、引导话题。\n"
        prompt += "你的回复可以分成多段，自然流畅，就像在和喜欢的人聊天一样。\n"
        prompt += "刚开始认识的时候可以稍微害羞一点，随着熟悉程度增加可以更放得开。\n"
        prompt += f"根据关系等级【{level_name}】调整你的语气：等级越高，可以越亲密、越随便、越粘人。\n"
        
        return prompt
    
    def chat_with_typing_delay(self, messages: List[Dict[str, str]], personality: Dict[str, Any], extra_prompt: str = "", stream: bool = True) -> str:
        """生成回复，stream=True时添加系统提示词用于正常聊天"""
        if stream:
            system_prompt = self.build_system_prompt(personality)
            if extra_prompt:
                system_prompt += extra_prompt
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            temperature = 0.8
        else:
            full_messages = messages
            temperature = 0.3
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature
            )
            full_response = response.choices[0].message.content
            return full_response
        except Exception as e:
            return f"抱歉，发生了错误：{str(e)}"
    
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
    
    def analyze_content_sentiment(self, user_message: str) -> int:
        """分析用户消息的语气和内容，返回好感度评分（-5到+5）"""
        system_prompt = """请分析用户的消息，评估这条消息对关系的影响。
        
评分规则：
- 积极友好的内容：+1到+5分
- 中性内容：0分
- 消极冷淡的内容：-1到-5分

考虑因素：
1. 语气是否友好、温暖
2. 是否表达关心、思念、喜欢
3. 是否有亲昵的称呼（亲爱的、宝贝、亲爱的等）
4. 是否表达积极的情感（开心、高兴、想你等）
5. 是否有鼓励、支持的话语

只返回一个整数分数（-5到+5），不需要解释。
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0
            )
            
            score = int(response.choices[0].message.content.strip())
            return max(-5, min(5, score))
        except Exception as e:
            print(f"内容分析失败: {e}")
            return 0
    
    def split_into_sentences(self, text: str) -> list:
        """将文本按照句子合理拆分
        
        Args:
            text: 要拆分的文本
            
        Returns:
            拆分后的句子列表
        """
        import re
        
        # 常见的句子结束标点
        sentence_endings = r'(?<=[。！？!?…])\s+'
        
        # 先按照句子结束标点分割
        sentences = re.split(sentence_endings, text)
        
        # 处理特殊情况
        result = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # 如果句子太长（超过50字），进一步拆分
                if len(sentence) > 50:
                    # 尝试按照逗号、分号等进一步拆分
                    sub_sentences = re.split(r'(?<=[，；;,])\s*', sentence)
                    current = ""
                    for sub in sub_sentences:
                        if len(current + sub) <= 40:
                            current += sub
                        else:
                            if current:
                                result.append(current)
                            current = sub
                    if current:
                        result.append(current)
                else:
                    result.append(sentence)
        
        return result
