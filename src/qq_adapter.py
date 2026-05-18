
import threading
import time
import json
from datetime import datetime
from typing import Optional, Callable

try:
    import requests
    import websockets
    import asyncio
    QQ_AVAILABLE = True
except ImportError:
    QQ_AVAILABLE = False


class QQAdapter:
    """QQ适配器，基于 go-cqhttp 的 HTTP/WebSocket API"""
    
    def __init__(self, http_url: str = "http://127.0.0.1:8080", ws_url: str = "ws://127.0.0.1:8080/ws"):
        """
        初始化QQ适配器
        
        Args:
            http_url: go-cqhttp 的 HTTP 接口地址
            ws_url: go-cqhttp 的 WebSocket 接口地址
        """
        if not QQ_AVAILABLE:
            raise ImportError("请先安装依赖库: pip install requests websockets")
        
        self.http_url = http_url.rstrip('/')
        self.ws_url = ws_url
        self.target_id: Optional[int] = None
        self.target_type: str = "private"  # "private" 私聊 "group" 群聊
        self.on_message_callback: Optional[Callable] = None
        self.is_connected = False
        self.ws = None
        self.running = False
        
    def test_connection(self) -> bool:
        """
        测试与 go-cqhttp 的连接
        
        Returns:
            连接是否成功
        """
        try:
            response = requests.get(f"{self.http_url}/get_status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('online', False):
                    self.is_connected = True
                    return True
            return False
        except Exception as e:
            print(f"连接测试失败: {e}")
            return False
    
    def set_target(self, qq_number: int, target_type: str = "private"):
        """
        设置聊天目标
        
        Args:
            qq_number: QQ号或群号
            target_type: "private" 私聊或 "group" 群聊
        """
        self.target_id = qq_number
        self.target_type = target_type
        print(f"✅ 聊天目标设置为: {target_type} - {qq_number}")
    
    def send_private_msg(self, user_id: int, message: str) -> bool:
        """
        发送私聊消息
        
        Args:
            user_id: QQ号
            message: 消息内容
            
        Returns:
            是否发送成功
        """
        try:
            data = {
                "user_id": user_id,
                "message": message
            }
            response = requests.post(f"{self.http_url}/send_private_msg", json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"发送失败: {e}")
            return False
    
    def send_group_msg(self, group_id: int, message: str) -> bool:
        """
        发送群聊消息
        
        Args:
            group_id: 群号
            message: 消息内容
            
        Returns:
            是否发送成功
        """
        try:
            data = {
                "group_id": group_id,
                "message": message
            }
            response = requests.post(f"{self.http_url}/send_group_msg", json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"发送失败: {e}")
            return False
    
    def send_message(self, message: str) -> bool:
        """
        发送消息到目标
        
        Args:
            message: 消息内容
            
        Returns:
            是否发送成功
        """
        if not self.target_id:
            print("❌ 未设置聊天目标")
            return False
            
        if self.target_type == "private":
            return self.send_private_msg(self.target_id, message)
        else:
            return self.send_group_msg(self.target_id, message)
    
    def register_message_callback(self, callback: Callable):
        """
        注册消息回调函数
        
        Args:
            callback: 回调函数，签名: callback(message_content, sender_id)
        """
        self.on_message_callback = callback
    
    async def _ws_listener(self):
        """WebSocket 监听异步任务"""
        try:
            async with websockets.connect(self.ws_url) as ws:
                self.ws = ws
                print("✅ WebSocket 连接成功")
                while self.running:
                    try:
                        message = await ws.recv()
                        await self._handle_ws_message(message)
                    except websockets.exceptions.ConnectionClosed:
                        print("❌ WebSocket 连接断开")
                        break
                    except Exception as e:
                        print(f"❌ WebSocket 错误: {e}")
        except Exception as e:
            print(f"❌ WebSocket 连接失败: {e}")
    
    async def _handle_ws_message(self, message: str):
        """处理接收到的 WebSocket 消息"""
        try:
            data = json.loads(message)
            if data.get('post_type') == 'message':
                message_type = data.get('message_type')
                user_id = data.get('user_id')
                content = data.get('message', '')
                
                # 只处理目标消息
                if self.target_id:
                    if message_type == 'private' and user_id == self.target_id and self.target_type == 'private':
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] QQ({user_id}): {content}")
                        if self.on_message_callback:
                            self.on_message_callback(content, user_id)
                    elif message_type == 'group' and data.get('group_id') == self.target_id and self.target_type == 'group':
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 群聊({data.get('group_id')}) QQ({user_id}): {content}")
                        if self.on_message_callback:
                            self.on_message_callback(content, user_id)
        except Exception as e:
            print(f"消息处理错误: {e}")
    
    def _run_ws_loop(self):
        """在单独线程中运行 WebSocket 循环"""
        asyncio.run(self._ws_listener())
    
    def start_listening(self):
        """开始监听消息"""
        if not self.test_connection():
            print("❌ 无法连接到 go-cqhttp，请检查是否已启动")
            return False
        
        self.running = True
        ws_thread = threading.Thread(target=self._run_ws_loop, daemon=True)
        ws_thread.start()
        
        print("✅ QQ适配器已启动")
        return True
    
    def stop(self):
        """停止QQ适配器"""
        self.running = False


class QQChatManager:
    """QQ聊天管理器，整合QQ适配器和千语系统"""
    
    def __init__(self, memory_manager, llm_client, scheduler):
        """
        初始化聊天管理器
        
        Args:
            memory_manager: 记忆管理器
            llm_client: LLM客户端
            scheduler: 调度器
        """
        self.memory_manager = memory_manager
        self.llm_client = llm_client
        self.scheduler = scheduler
        self.qq_adapter = QQAdapter()
        self.personality = memory_manager.load_personality()
        
        self.is_running = False
        self.message_lock = threading.Lock()
        
    def start(self, target_qq: int, target_type: str = "private", 
              http_url: str = "http://127.0.0.1:8080", 
              ws_url: str = "ws://127.0.0.1:8080/ws"):
        """
        启动QQ聊天系统
        
        Args:
            target_qq: 目标QQ号或群号
            target_type: "private" 私聊或 "group" 群聊
            http_url: go-cqhttp 的 HTTP 接口地址
            ws_url: go-cqhttp 的 WebSocket 接口地址
        """
        print("=" * 50)
        print("千语 - QQ版")
        print("=" * 50)
        
        # 初始化状态
        self.is_running = True
        
        # 重新初始化QQ适配器
        self.qq_adapter = QQAdapter(http_url, ws_url)
        
        # 注册消息回调
        self.qq_adapter.register_message_callback(self._handle_user_message)
        
        # 设置聊天目标
        self.qq_adapter.set_target(target_qq, target_type)
        
        # 启动监听
        if not self.qq_adapter.start_listening():
            print("❌ QQ适配器启动失败")
            return
        
        # 启动主动消息线程
        proactive_thread = threading.Thread(target=self._proactive_message_loop, daemon=True)
        proactive_thread.start()
        
        # 发送问候
        self._send_greeting()
        
        # 保持主线程运行
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n收到中断信号")
            self.stop()
    
    def _send_greeting(self):
        """发送问候消息"""
        zip_history = self.memory_manager.load_zip_history()
        is_first_chat = (len(zip_history.get("summaries", [])) == 0)
        
        if is_first_chat:
            greeting = self.personality.get("greeting", "你好！")
            self._send_typing_message(greeting)
        else:
            self._send_typing_message("我回来啦！😊")
    
    def _handle_user_message(self, content: str, sender_id: int):
        """
        处理用户消息
        
        Args:
            content: 消息内容
            sender_id: 发送者QQ号
        """
        # 处理命令
        if content == '/状态' or content == '/stats':
            self._show_status()
            return
        if content == '/浓缩' or content == '/summary':
            self._do_summary()
            return
        
        with self.message_lock:
            # 更新最后消息时间
            self.scheduler.update_last_message_time()
            
            # 保存用户消息
            self.memory_manager.add_chat_message("user", content)
            
            # 分析语气并增加经验值
            sentiment_score = self.llm_client.analyze_content_sentiment(content)
            if sentiment_score != 0:
                self.memory_manager.add_content_bonus(sentiment_score)
            
            # 获取上下文并生成回复
            context_messages = self.memory_manager.get_context_messages()
            full_response = self.llm_client.chat_with_typing_delay(
                context_messages, self.personality
            )
            
            # 发送回复
            self._send_typing_message(full_response)
            
            # 保存助手回复
            self.memory_manager.add_chat_message("assistant", full_response)
            
            # 更新最后消息时间
            self.scheduler.update_last_message_time()
            
            # 显示关系状态
            level = self.memory_manager.get_relationship_level()
            exp = self.memory_manager.get_experience()
            level_names = self.memory_manager.LEVEL_NAMES
            print(f"\n当前状态: 【{level_names[level]}】- {exp}EXP")
    
    def _send_typing_message(self, content: str):
        """
        模拟打字并发送消息
        
        Args:
            content: 消息内容
        """
        # 计算打字时间
        typing_time = self.llm_client.calculate_typing_delay(content)
        
        # 显示正在输入提示（在控制台）
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 千语正在输入...")
        
        # 等待打字时间
        time.sleep(typing_time)
        
        # 发送消息
        self.qq_adapter.send_message(content)
        
        # 显示发送的消息
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 千语: {content}")
    
    def _show_status(self):
        """显示当前状态"""
        stats = self.memory_manager.get_stats()
        level = self.memory_manager.get_relationship_level()
        exp = self.memory_manager.get_experience()
        level_names = self.memory_manager.LEVEL_NAMES
        
        status_msg = f"📊 当前状态\n\n"
        status_msg += f"日期: {stats.get('today')}\n"
        status_msg += f"今日聊天: {stats.get('today_chat_count')} 条\n"
        status_msg += f"关系等级: 【{level_names[level]}】\n"
        status_msg += f"经验值: {exp} EXP\n"
        status_msg += f"总摘要: {stats.get('total_summaries')} 条\n"
        status_msg += f"核心事件: {stats.get('total_events')} 个"
        
        print(f"\n{status_msg}")
        self.qq_adapter.send_message(status_msg)
    
    def _do_summary(self):
        """手动浓缩"""
        from src.summary_agent import SummaryAgent
        print("正在浓缩...")
        self.qq_adapter.send_message("正在浓缩聊天记录，请稍候...")
        
        summary_agent = SummaryAgent(self.llm_client, self.memory_manager)
        result = summary_agent.run_summary()
        
        if result.get("status") == "success":
            msg = f"✅ 浓缩完成！\n处理了 {len(result.get('summarized_dates', []))} 天的记录"
        else:
            msg = "✅ 没有需要浓缩的记录"
        
        print(msg)
        self.qq_adapter.send_message(msg)
    
    def _proactive_message_loop(self):
        """主动消息循环"""
        while self.is_running:
            try:
                # 检查是否有待发送的主动消息
                pending_msg = self.scheduler.get_pending_message()
                if pending_msg:
                    self._send_typing_message(pending_msg)
                    self.memory_manager.add_chat_message("assistant", pending_msg)
                    self.scheduler.update_last_message_time()
                
                time.sleep(1)
            except Exception as e:
                print(f"主动消息循环错误: {e}")
                time.sleep(1)
    
    def stop(self):
        """停止聊天系统"""
        self.is_running = False
        self.qq_adapter.stop()
