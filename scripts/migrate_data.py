#!/usr/bin/env python3
import os
import shutil
import json
from datetime import datetime
from src.memory_manager import MemoryManager


def migrate_old_data():
    """从旧格式数据迁移到新系统"""
    print("=" * 50)
    print("正在检查旧格式数据...")
    print("=" * 50)
    
    old_data_dir = "data"
    old_chat_file = os.path.join(old_data_dir, "chat_history", "chat_history.json")
    old_summaries_file = os.path.join(old_data_dir, "summarized_memory", "summarized_memory.json")
    
    if os.path.exists(old_chat_file):
        print(f"\n找到旧聊天记录文件: {old_chat_file}")
        
        try:
            with open(old_chat_file, 'r', encoding='utf-8') as f:
                old_chat = json.load(f)
            
            if old_chat:
                today = datetime.now().strftime("%Y-%m-%d")
                new_chat_file = os.path.join(old_data_dir, "chat_history", f"chat_history_{today}.json")
                
                if not os.path.exists(new_chat_file):
                    print(f"迁移到: {new_chat_file}")
                    os.makedirs(os.path.dirname(new_chat_file), exist_ok=True)
                    with open(new_chat_file, 'w', encoding='utf-8') as f:
                        json.dump(old_chat, f, ensure_ascii=False, indent=2)
                    print("✓ 聊天记录已迁移")
                else:
                    print("✓ 今日聊天记录文件已存在")
                
                backup_file = old_chat_file + ".backup"
                if not os.path.exists(backup_file):
                    shutil.copy2(old_chat_file, backup_file)
                    print(f"✓ 已备份旧文件到: {backup_file}")
        except Exception as e:
            print(f"迁移聊天记录出错: {e}")
    
    if os.path.exists(old_summaries_file):
        print(f"\n找到旧摘要文件: {old_summaries_file}")
        
        try:
            with open(old_summaries_file, 'r', encoding='utf-8') as f:
                old_summaries = json.load(f)
            
            zip_file = os.path.join(old_data_dir, "chat_history_zip.json")
            
            if not os.path.exists(zip_file) and old_summaries:
                print("迁移到新格式...")
                
                new_zip_data = {
                    "summaries": [],
                    "core_events": []
                }
                
                for summary_item in old_summaries[-20:]:
                    new_zip_data["summaries"].append({
                        "date": summary_item.get("date", ""),
                        "summary": summary_item.get("summary", ""),
                        "timestamp": datetime.now().isoformat()
                    })
                
                with open(zip_file, 'w', encoding='utf-8') as f:
                    json.dump(new_zip_data, f, ensure_ascii=False, indent=2)
                
                print("✓ 摘要已迁移")
        except Exception as e:
            print(f"迁移摘要出错: {e}")
    
    print("\n" + "=" * 50)
    print("迁移完成！")
    print("=" * 50)


if __name__ == "__main__":
    migrate_old_data()
