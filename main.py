#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from src.memory_manager import MemoryManager
from src.llm_client import LLMClient
from src.scheduler import Scheduler


# 加载 .env 文件中的环境变量
load_dotenv()


def main():
    """主程序入口，初始化组件并处理聊天流程"""
    print("=" * 50)
    print("聊天助手启动中...")
    print("=" * 50)
    
    # 初始化记忆管理器
    memory_manager = MemoryManager()
    personality = memory_manager.load_personality()
    
    # 初始化LLM客户端
    llm_client = LLMClient()
    
    # 初始化并启动定时任务调度器
    scheduler = Scheduler(memory_manager, llm_client)
    scheduler.start()
    
    # 检查是否是第一次聊天，如果是则发送问候语
    chat_history = memory_manager.load_chat_history()
    if not chat_history:
        greeting = personality.get("greeting", "你好！")
        print(f"\n{personality.get('name', '小助手')}: {greeting}")
        memory_manager.add_chat_message("assistant", greeting)
    else:
        print(f"\n欢迎回来！已有 {len(chat_history)} 条聊天记录")
    
    try:
        # 主聊天循环
        while True:
            user_input = input("\n你: ").strip()
            
            # 处理退出命令
            if user_input.lower() in ['退出', 'exit', 'quit', 'q']:
                print("再见！")
                break
            
            # 处理总结命令
            if user_input.lower() in ['总结', 'summary']:
                print("正在生成聊天摘要...")
                scheduler.trigger_summary_now()
                continue
            
            # 忽略空输入
            if not user_input:
                continue
            
            # 保存用户消息
            memory_manager.add_chat_message("user", user_input)
            
            # 获取上下文消息
            context_messages = memory_manager.get_context_messages()
            
            # 流式输出助手回复
            print(f"\n{personality.get('name', '小助手')}: ", end="", flush=True)
            
            full_response = ""
            for chunk in llm_client.chat_stream(context_messages, personality):
                print(chunk, end="", flush=True)
                full_response += chunk
            print()
            
            # 保存助手回复
            memory_manager.add_chat_message("assistant", full_response)
            
    except KeyboardInterrupt:
        print("\n\n收到中断信号，正在退出...")
    finally:
        # 清理资源
        scheduler.stop()
        print("聊天助手已关闭")


if __name__ == "__main__":
    main()
