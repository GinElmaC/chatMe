import threading
import time
import random
from datetime import datetime, timedelta
from typing import Callable
from src.memory_manager import MemoryManager
from src.llm_client import LLMClient


class Scheduler:
    """定时任务调度器，定期重新加载配置和生成每日摘要，还能主动发起对话"""
    
    def __init__(self, memory_manager: MemoryManager, llm_client: LLMClient):
        """初始化调度器，设置依赖的管理器实例"""
        self.memory_manager = memory_manager
        self.llm_client = llm_client
        self.running = False
        self.threads = []
        self.last_summary_date = None
        self.last_message_time = datetime.now()
        self.pending_message = None
        self.message_lock = threading.Lock()
        self.next_proactive_time = self._calculate_next_proactive_time()
        # 追问相关
        self.waiting_for_reply = False
        self.last_proactive_message_time = None
        self.follow_up_attempts = 0
        # 打字延迟相关
        self.is_typing = False
        self.typing_end_time = None
    
    def _get_relationship_params(self):
        """根据关系等级获取参数"""
        level = self.memory_manager.get_relationship_level()
        exp = self.memory_manager.get_experience()
        level_name = self.memory_manager.LEVEL_NAMES[level]
        
        # 关系等级 0-4（陌生、熟悉、有好感、亲密、交往）
        # 等级越高，追问越频繁，次数越多
        
        # 主动消息间隔（分钟）：等级越高，间隔越短
        if level == 0:
            proactive_min = 60  # 1-4小时
            proactive_max = 240
        elif level == 1:
            proactive_min = 45
            proactive_max = 180
        elif level == 2:
            proactive_min = 30
            proactive_max = 150
        elif level == 3:
            proactive_min = 20
            proactive_max = 120
        else:  # level 4（交往）
            proactive_min = 10
            proactive_max = 90
        
        # 追问阈值（分钟）：等级越高，越容易追问
        if level == 0:
            follow_up_threshold = 60  # 1小时才追问
            max_follow_ups = 1
        elif level == 1:
            follow_up_threshold = 45
            max_follow_ups = 1
        elif level == 2:
            follow_up_threshold = 30
            max_follow_ups = 2
        elif level == 3:
            follow_up_threshold = 20
            max_follow_ups = 2
        else:  # level 4（交往）
            follow_up_threshold = 15
            max_follow_ups = 3
        
        return {
            "proactive_min": proactive_min,
            "proactive_max": proactive_max,
            "follow_up_threshold": follow_up_threshold,
            "max_follow_ups": max_follow_ups,
            "level": level,
            "level_name": level_name,
            "experience": exp
        }
    
    def start_typing(self, text: str):
        """开始打字计时，设置打字结束时间"""
        delay = self.llm_client.calculate_typing_delay(text)
        self.is_typing = True
        self.typing_end_time = datetime.now() + timedelta(seconds=delay)
        print(f"⌨️ 正在输入... (约{int(delay)}秒)")
        return delay
    
    def end_typing(self):
        """结束打字，重置追问计时"""
        self.is_typing = False
        self.typing_end_time = None
        # 重置追问时间
        if self.waiting_for_reply:
            self.last_proactive_message_time = datetime.now()
    
    def start(self):
        """启动配置重新加载和每日摘要两个后台线程"""
        if self.running:
            return
        
        self.running = True
        
        reload_thread = threading.Thread(target=self._reload_config_task, daemon=True)
        reload_thread.start()
        self.threads.append(reload_thread)
        
        summary_thread = threading.Thread(target=self._daily_summary_task, daemon=True)
        summary_thread.start()
        self.threads.append(summary_thread)
        
        # 主动对话线程
        proactive_thread = threading.Thread(target=self._proactive_chat_task, daemon=True)
        proactive_thread.start()
        self.threads.append(proactive_thread)
    
    def stop(self):
        """停止定时任务，等待所有线程退出"""
        self.running = False
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1.0)
    
    def _reload_config_task(self):
        """每60秒重新加载人格设定"""
        while self.running:
            try:
                self.memory_manager.load_personality()
                self.memory_manager.load_zip_history()
            except Exception as e:
                print(f"重新加载配置失败: {e}")
            
            for _ in range(60):
                if not self.running:
                    break
                time.sleep(1)
    
    def _daily_summary_task(self):
        """每日摘要任务（在新系统中已废弃，保留空循环）"""
        while self.running:
            try:
                pass
            except Exception as e:
                print(f"任务循环失败: {e}")
            
            for _ in range(300):
                if not self.running:
                    break
                time.sleep(1)
    
    def _is_active_time(self):
        """检查当前时间是否适合主动发消息（8:00-24:00）"""
        now = datetime.now()
        hour = now.hour
        return 8 <= hour < 24
    
    def _calculate_next_proactive_time(self):
        """计算下一次主动发消息的时间（根据关系等级的随机间隔）"""
        params = self._get_relationship_params()
        random_minutes = random.uniform(params["proactive_min"], params["proactive_max"])
        delay_seconds = random_minutes * 60
        return datetime.now() + timedelta(seconds=delay_seconds)
    
    def _proactive_chat_task(self):
        """主动对话任务：在合适的时间主动发起对话"""
        while self.running:
            try:
                now = datetime.now()
                params = self._get_relationship_params()
                
                # 检查是否在打字中，如果在打字跳过检查追问
                if self.is_typing and self.typing_end_time:
                    if now < self.typing_end_time:
                        # 还在打字中
                        time.sleep(0.1)
                        continue
                    else:
                        # 打字结束
                        self.is_typing = False
                        self.typing_end_time = None
                
                # 检查是否需要追问
                if self.waiting_for_reply and self.last_proactive_message_time:
                    time_since_proactive = (now - self.last_proactive_message_time).total_seconds()
                    threshold_seconds = params["follow_up_threshold"] * 60
                    
                    if time_since_proactive >= threshold_seconds:
                        if self.follow_up_attempts < params["max_follow_ups"]:
                            # 追问
                            self._generate_follow_up_message()
                            self.follow_up_attempts += 1
                            self.last_proactive_message_time = now
                            
                            # 第二次及以后的追问，扣经验值
                            if self.follow_up_attempts >= 2:
                                self.memory_manager.add_follow_up_penalty()
                                print(f"⏳ 第二次追问，经验值 -2")
                
                # 检查是否是活跃时间，且到达了主动对话时间，且不在等待回复
                if self._is_active_time() and now >= self.next_proactive_time and not self.waiting_for_reply:
                    # 检查是否有一段时间没说话了（至少1小时）
                    time_since_last_message = (now - self.last_message_time).total_seconds()
                    if time_since_last_message >= 3600:
                        self._generate_proactive_message()
                        self.waiting_for_reply = True
                        self.last_proactive_message_time = now
                        self.follow_up_attempts = 0
                    
                    # 计算下一次主动对话时间
                    self.next_proactive_time = self._calculate_next_proactive_time()
                    print(f"下次主动对话时间: {self.next_proactive_time.strftime('%H:%M')} ({params['level_name']} - {params['experience']}EXP)")
                
            except Exception as e:
                print(f"主动对话任务失败: {e}")
            
            for _ in range(60):
                if not self.running:
                    break
                time.sleep(1)
    
    def _generate_follow_up_message(self):
        """生成追问消息，根据关系等级调整语气"""
        personality = self.memory_manager.load_personality()
        name = personality.get('name', '千语')
        level = self.memory_manager.get_relationship_level()
        level_name = self.memory_manager.LEVEL_NAMES[level]
        
        # 根据关系等级调整撒娇程度
        if level >= 3:
            clingy_level = "很粘人，撒娇感很强"
        elif level >= 2:
            clingy_level = "有点粘人，带点撒娇"
        else:
            clingy_level = "比较矜持，温柔询问"
        
        system_prompt = f"""你是{name}，你刚才给用户发了消息，但用户一直没回复。
现在你要追问一下。

【关系等级】{level_name}
【粘人程度】{clingy_level}

要求：
- 根据关系等级调整语气，等级越高越可以撒娇
- 可以问对方在干嘛，是不是在忙
- 不要太烦人，但可以表现出想念
- 一句话就好，不要太长
- 用自然的语气

【例子】
陌生/熟悉: "哈喽~ 还在吗？是不是在忙呀？"
有好感: "你在干嘛呢？怎么不理我了😢"
亲密/交往: "呜呜…你都不理我了，在忙什么呀？🥺"
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        try:
            response = self.llm_client.chat(messages, personality)
            if response and not response.startswith("抱歉"):
                with self.message_lock:
                    self.pending_message = response
                print(f"生成追问消息 ({level_name}): {response}")
        except Exception as e:
            print(f"生成追问消息失败: {e}")
    
    def _generate_proactive_message(self):
        """生成主动发起的对话内容，结合自身情况和聊天记录"""
        personality = self.memory_manager.load_personality()
        chat_history = self.memory_manager.load_today_chat_history()
        zip_history = self.memory_manager.load_zip_history()
        name = personality.get('name', '千语')
        level = self.memory_manager.get_relationship_level()
        level_name = self.memory_manager.LEVEL_NAMES[level]
        
        # 获取当前时间和状态
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        # 构建更丰富的提示词
        context = f"""当前时间: {now.strftime('%Y-%m-%d %H:%M')}
今天是: {weekdays[weekday]}
当前时段: {'上午' if 8 <= hour < 12 else '下午' if 12 <= hour < 18 else '晚上'}
"""
        
        # 获取最近的聊天记录摘要
        recent_chats = []
        if chat_history:
            recent_chats = chat_history[-10:]
        
        # 从聊天记录中提取关键信息
        recent_topics = []
        for msg in recent_chats:
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                if len(content) > 5:
                    recent_topics.append(content[:30])
        
        # 从人格设定中获取当前状态和爱好
        current_status = personality.get('current_status', '')
        hobbies = personality.get('hobbies', [])
        user_description = personality.get('user_description', '')
        
        # 根据关系等级调整亲密程度
        if level >= 3:
            intimacy_level = "很亲密，可以更随便、更粘人一点"
        elif level >= 2:
            intimacy_level = "比较熟悉，可以更亲近一些"
        else:
            intimacy_level = "刚认识不久，保持礼貌和温柔"
        
        # 构建更详细的提示词
        system_prompt = f"""你是{name}，现在你主动找用户聊天。

【当前场景】
{context}

【关系等级】{level_name}
【亲密程度】{intimacy_level}

【你的状态】
{current_status}

【你的爱好】
{'、'.join(hobbies) if hobbies else '没有特别记录'}

【你和用户的关系】
{user_description}

【最近的聊天话题】
{'、'.join(recent_topics) if recent_topics else '暂时没有特别的记录'}

【聊天要求】
1. 你现在是主动找用户聊天，不是回复消息
2. 语气要自然，像真的朋友一样，不要太正式
3. 可以结合当前时间问候（比如：早上好、下午好、晚上好）
4. 可以分享自己现在正在做的小事（比如：刚吃完饭、在看书、在喝奶茶等）
5. 可以关心一下对方的近况
6. 可以提到最近聊过的话题（如果有的话）
7. 可以问对方现在在做什么
8. 不要太刻意，要自然，像朋友之间的日常聊天
9. 一句话或两句话就好，不要太长
10. 可以用一些语气词（呀、呢、哦、哈、啦）
11. 可以用简单的表情（~、😊、✨）
12. 要符合你的性格特点
13. 根据关系等级调整语气：等级越高，可以越亲密、越随便、越粘人

【不要这样说】
❌ "在吗？"
❌ "你好，在吗？"
❌ "有空吗？"
❌ "打扰了"

【可以这样说】
✅ "嗨，在干嘛呢？我刚喝了杯奶茶，感觉好幸福~"
✅ "对了，你上次说的那个事情怎么样了呀？"
✅ "突然想到你，就来打个招呼~ 最近忙不忙？"
✅ "晚上好呀，我正在看书呢，你呢？"
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        try:
            response = self.llm_client.chat(messages, personality)
            if response and not response.startswith("抱歉"):
                with self.message_lock:
                    self.pending_message = response
                print(f"生成主动消息 ({level_name}): {response}")
        except Exception as e:
            print(f"生成主动消息失败: {e}")
    
    def get_pending_message(self):
        """获取待发送的主动消息（如果有的话）"""
        with self.message_lock:
            msg = self.pending_message
            self.pending_message = None
            return msg
    
    def update_last_message_time(self):
        """更新最后一条消息的时间（用户回复了）"""
        self.last_message_time = datetime.now()
        # 用户回复了，取消等待回复状态
        self.waiting_for_reply = False
        self.follow_up_attempts = 0
    
    def trigger_summary_now(self):
        """立即触发浓缩（在新系统中已废弃，保留方法兼容）"""
        print("请使用聊天命令 '浓缩' 或 'summary' 来触发浓缩")
