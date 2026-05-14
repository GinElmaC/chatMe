#!/usr/bin/env python3
"""
清理测试产生的临时数据
"""
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.memory_manager import MemoryManager

def cleanup_test_data():
    print("清理测试数据...")
    
    mm = MemoryManager()
    
    # 读取今日聊天记录
    today_history = mm.load_today_chat_history()
    
    # 只删除测试消息
    new_history = []
    test_found = False
    for msg in today_history:
        content = msg.get("content", "")
        if "这是一条测试消息" in content or "测试回复" in content:
            test_found = True
        else:
            new_history.append(msg)
    
    if test_found:
        mm.save_today_chat_history(new_history)
        print(f"✓ 已清理测试消息，今日还剩 {len(new_history)} 条消息")
    else:
        print("没有找到测试消息")
    
    print("清理完成！")

if __name__ == "__main__":
    cleanup_test_data()
