
#!/usr/bin/env python3
import os
import sys
import atexit
from dotenv import load_dotenv
from src.memory_manager import MemoryManager
from src.llm_client import LLMClient
from src.scheduler import Scheduler
from src.summary_agent import SummaryAgent
from src.qq_adapter import QQChatManager


# 加载 .env 文件中的环境变量
load_dotenv()


def main():
    """QQ版本主程序入口"""
    print("=" * 50)
    print("千语 - QQ版")
    print("=" * 50)
    
    # 获取参数
    target_qq = None
    target_type = "private"
    http_url = "http://127.0.0.1:8080"
    ws_url = "ws://127.0.0.1:8080/ws"
    
    if len(sys.argv) >= 2:
        if len(sys.argv) >= 3 and sys.argv[2] in ["private", "group"]:
            target_type = sys.argv[2]
        try:
            target_qq = int(sys.argv[1])
            print(f"从命令行参数获取目标: {target_type} - {target_qq}")
        except ValueError:
            pass
    
    if not target_qq:
        print("\n请输入聊天目标QQ号:")
        try:
            target_qq = int(input("QQ号: ").strip())
        except ValueError:
            print("❌ 无效的QQ号")
            return
        
        print("\n请选择聊天类型:")
        print("1. 私聊 (private)")
        print("2. 群聊 (group)")
        choice = input("请选择 (1/2): ").strip()
        if choice == "2":
            target_type = "group"
    
    # 初始化记忆管理器
    memory_manager = MemoryManager()
    personality = memory_manager.load_personality()
    
    # 获取当前关系状态
    level = memory_manager.get_relationship_level()
    exp = memory_manager.get_experience()
    level_names = MemoryManager.LEVEL_NAMES
    
    # 获取统计信息
    stats = memory_manager.get_stats()
    print(f"\n当前日期: {stats.get('today')}")
    print(f"今日聊天数: {stats.get('today_chat_count')}")
    print(f"已有摘要数: {stats.get('total_summaries')}")
    if stats.get('uncompressed_dates'):
        print(f"待浓缩日期: {', '.join(stats.get('uncompressed_dates'))}")
    
    print(f"\n当前关系状态:【{level_names[level]}】- {exp}EXP")
    
    # 初始化LLM客户端
    llm_client = LLMClient()
    
    # 初始化并启动定时任务调度器
    scheduler = Scheduler(memory_manager, llm_client)
    scheduler.start()
    
    # 初始化QQ聊天管理器
    chat_manager = QQChatManager(memory_manager, llm_client, scheduler)
    
    # 退出时执行浓缩
    def run_on_exit():
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
        chat_manager.stop()
        print("千语已安全关闭")
    
    atexit.register(run_on_exit)
    
    # 启动QQ聊天
    try:
        chat_manager.start(
            target_qq=target_qq,
            target_type=target_type,
            http_url=http_url,
            ws_url=ws_url
        )
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
