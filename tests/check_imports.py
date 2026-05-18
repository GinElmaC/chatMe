#!/usr/bin/env python3
"""
快速导入检查
"""
print("检查所有模块导入...")

print("1. 导入 MemoryManager...")
from src.memory_manager import MemoryManager
print("   ✓")

print("2. 导入 LLMClient...")
from src.llm_client import LLMClient
print("   ✓")

print("3. 导入 Scheduler...")
from src.scheduler import Scheduler
print("   ✓")

print("4. 导入 SummaryAgent...")
from src.summary_agent import SummaryAgent
print("   ✓")

print("\n✅ 所有模块导入成功！")
