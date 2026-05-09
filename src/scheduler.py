import threading
import time
from datetime import datetime, timedelta
from typing import Callable
from src.memory_manager import MemoryManager
from src.llm_client import LLMClient


class Scheduler:
    """定时任务调度器，定期重新加载配置和生成每日摘要"""
    
    def __init__(self, memory_manager: MemoryManager, llm_client: LLMClient):
        """初始化调度器，设置依赖的管理器实例"""
        self.memory_manager = memory_manager
        self.llm_client = llm_client
        self.running = False
        self.threads = []
        self.last_summary_date = None
    
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
    
    def stop(self):
        """停止定时任务，等待所有线程退出"""
        self.running = False
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1.0)
    
    def _reload_config_task(self):
        """每60秒重新加载人格设定和浓缩记忆"""
        while self.running:
            try:
                self.memory_manager.load_personality()
                self.memory_manager.load_summarized_memory()
            except Exception as e:
                print(f"重新加载配置失败: {e}")
            
            for _ in range(60):
                if not self.running:
                    break
                time.sleep(1)
    
    def _daily_summary_task(self):
        """每5分钟检查日期变化，发现新的一天则生成前一天摘要"""
        while self.running:
            try:
                now = datetime.now()
                current_date = now.strftime("%Y-%m-%d")
                
                if self.last_summary_date is None:
                    self.last_summary_date = current_date
                elif self.last_summary_date != current_date:
                    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
                    self._generate_daily_summary(yesterday)
                    self.last_summary_date = current_date
            except Exception as e:
                print(f"每日摘要任务失败: {e}")
            
            for _ in range(300):
                if not self.running:
                    break
                time.sleep(1)
    
    def _generate_daily_summary(self, date: str):
        """生成指定日期的聊天摘要，保存并清空历史"""
        print(f"正在生成 {date} 的聊天摘要...")
        
        chat_history = self.memory_manager.load_chat_history()
        if not chat_history:
            print("没有聊天记录需要总结")
            return
        
        summary = self.llm_client.summarize_chat(chat_history)
        chat_count = len(chat_history)
        
        self.memory_manager.add_summarized_memory(date, summary, chat_count)
        self.memory_manager.clear_chat_history()
        
        print(f"已生成 {date} 的聊天摘要，共 {chat_count} 条消息")
        print(f"摘要内容: {summary}")
    
    def trigger_summary_now(self):
        """立即触发当天的聊天摘要生成"""
        today = datetime.now().strftime("%Y-%m-%d")
        self._generate_daily_summary(today)
