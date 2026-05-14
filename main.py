#!/usr/bin/env python3
import os
import sys
import threading
import time
import atexit
from datetime import datetime
from dotenv import load_dotenv
from src.memory_manager import MemoryManager
from src.llm_client import LLMClient
from src.scheduler import Scheduler
from src.summary_agent import SummaryAgent


# 加载 .env 文件中的环境变量
load_dotenv()


def main():
    """主程序入口，初始化组件并处理聊天流程"""
    print("=" * 50)
    print("千语 - 新记忆系统启动中...")
    print("=" * 50)
    
    # 初始化记忆管理器
    memory_manager = MemoryManager()
    personality = memory_manager.load_personality()
    
    # 获取当前关系状态
    level = memory_manager.get_relationship_level()
    exp = memory_manager.get_experience()
    level_names = MemoryManager.LEVEL_NAMES
    
    # 获取统计信息
    stats = memory_manager.get_stats()
    print(f"\n当前日期: {stats['today']}")
    print(f"今日聊天数: {stats['today_chat_count']}")
    print(f"已有摘要数: {stats['total_summaries']}")
    if stats.get('uncompressed_dates'):
        print(f"待浓缩日期: {', '.join(stats['uncompressed_dates'])}")
    
    print(f"\n当前关系状态:【{level_names[level]}】- {exp}EXP")
    
    # 初始化LLM客户端
    llm_client = LLMClient()
    
    # 初始化并启动定时任务调度器
    scheduler = Scheduler(memory_manager, llm_client)
    scheduler.start()
    
    # 检查是否是第一次聊天，如果是则发送问候语
    today_history = memory_manager.load_today_chat_history()
    if not today_history:
        greeting = personality.get("greeting", "你好！")
        scheduler.start_typing(greeting)
        typing_time = llm_client.calculate_typing_delay(greeting)
        time.sleep(typing_time)
        print(f"\n{personality.get('name', '千语')}: {greeting}")
        scheduler.end_typing()
        memory_manager.add_chat_message("assistant", greeting)
    else:
        print(f"\n欢迎回来！今日已有 {len(today_history)} 条聊天记录")
    
    # 创建一个标志位来控制退出
    should_exit = False
    
    def check_proactive_message():
        """检查是否有主动消息需要显示"""
        nonlocal should_exit
        while not should_exit:
            try:
                pending_msg = scheduler.get_pending_message()
                if pending_msg:
                    scheduler.start_typing(pending_msg)
                    time.sleep(scheduler.llm_client.calculate_typing_delay(pending_msg))
                    print()
                    print(f"{personality.get('name', '千语')}: {pending_msg}")
                    scheduler.end_typing()
                    memory_manager.add_chat_message("assistant", pending_msg)
                    scheduler.update_last_message_time()
                    print("\n你: ", end="", flush=True)
                time.sleep(1)
            except Exception as e:
                print(f"\n检查主动消息出错: {e}")
                time.sleep(1)
    
    # 启动主动消息检查线程
    proactive_thread = threading.Thread(target=check_proactive_message, daemon=True)
    proactive_thread.start()
    
    def run_on_exit():
        """程序退出时执行浓缩"""
        print("\n" + "=" * 50)
        print("正在执行退出前的浓缩...")
        print("=" * 50)
        summary_agent = SummaryAgent(llm_client, memory_manager)
        result = summary_agent.run_summary()
        
        if result.get("status") == "success":
            print(f"✓ 成功浓缩了 {len(result.get('summarized_dates', []))} 天的记录")
        elif result.get("status") == "nothing_to_summarize":
            print("✓ 没有需要浓缩的记录")
        
        scheduler.stop()
        print("千语已安全关闭")
    
    atexit.register(run_on_exit)
    
    try:
        # 主聊天循环
        while not should_exit:
            try:
                user_input = input("\n你: ").strip()
                
                if user_input.lower() in ['退出', 'exit', 'quit', 'q']:
                    print("再见！")
                    should_exit = True
                    break
                
                if user_input.lower() in ['总结', 'summary', '浓缩']:
                    print("正在执行手动浓缩...")
                    summary_agent = SummaryAgent(llm_client, memory_manager)
                    result = summary_agent.run_summary()
                    if result.get("status") == "success":
                        print(f"✓ 浓缩完成！处理了 {len(result.get('summarized_dates', []))} 天的记录")
                    else:
                        print("没有需要浓缩的记录")
                    continue
                
                if user_input.lower() in ['状态', 'stats']:
                    stats = memory_manager.get_stats()
                    print("\n当前状态:")
                    print(f"  今日: {stats['today']}")
                    print(f"  今日聊天数: {stats['today_chat_count']}")
                    print(f"  总摘要数: {stats['total_summaries']}")
                    print(f"  核心事件数: {stats['total_events']}")
                    if stats.get('uncompressed_dates'):
                        print(f"  待浓缩日期: {', '.join(stats['uncompressed_dates'])}")
                    continue
                
                if not user_input:
                    continue
                
                # 更新最后消息时间
                scheduler.update_last_message_time()
                
                # 保存用户消息（这会自动增加1点经验值）
                memory_manager.add_chat_message("user", user_input)
                
                # 分析用户消息的语气，给予额外经验值
                sentiment_score = llm_client.analyze_content_sentiment(user_input)
                if sentiment_score != 0:
                    memory_manager.add_content_bonus(sentiment_score)
                    if sentiment_score > 0:
                        print(f"💕 好感度 +{sentiment_score}")
                    else:
                        print(f"💔 好感度 {sentiment_score}")
                
                # 获取上下文消息
                context_messages = memory_manager.get_context_messages()
                
                # 先获取完整回复
                full_response = llm_client.chat_with_typing_delay(context_messages, personality)
                
                # 计算打字延迟
                scheduler.start_typing(full_response)
                
                # 等待打字时间
                typing_time = llm_client.calculate_typing_delay(full_response)
                time.sleep(typing_time)
                
                # 一次性显示回复
                print(f"\n{personality.get('name', '千语')}: {full_response}")
                
                # 结束打字，重置追问计时
                scheduler.end_typing()
                
                # 保存助手回复
                memory_manager.add_chat_message("assistant", full_response)
                
                # 更新最后消息时间
                scheduler.update_last_message_time()
                
                # 显示当前关系状态
                level = memory_manager.get_relationship_level()
                exp = memory_manager.get_experience()
                print(f"\n💗 当前状态: 【{level_names[level]}】- {exp}EXP")
                
            except KeyboardInterrupt:
                print("\n\n收到中断信号，正在准备退出...")
                should_exit = True
                break
            except Exception as e:
                print(f"\n发生错误: {e}")
                continue
                
    finally:
        # 清理资源
        should_exit = True


if __name__ == "__main__":
    main()
