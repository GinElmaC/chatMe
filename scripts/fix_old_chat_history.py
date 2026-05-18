
import json
import os
from datetime import datetime

# 路径
old_file = "data/chat_history/chat_history.json"
today = datetime.now().strftime("%Y-%m-%d")
today_file = f"data/chat_history/chat_history_{today}.json"
backup_file = f"data/chat_history/chat_history.json.bak"

if os.path.exists(old_file):
    # 读取旧文件
    with open(old_file, 'r', encoding='utf-8') as f:
        old_history = json.load(f)
    
    print(f"发现旧聊天记录文件，包含 {len(old_history)} 条消息")
    
    # 读取今天的聊天记录（如果存在）
    today_history = []
    if os.path.exists(today_file):
        with open(today_file, 'r', encoding='utf-8') as f:
            today_history = json.load(f)
    
    # 合并消息，确保按时间排序
    all_messages = today_history + old_history
    # 按 timestamp 排序
    all_messages.sort(key=lambda x: x.get('timestamp', ''))
    
    # 保存到今天的文件
    with open(today_file, 'w', encoding='utf-8') as f:
        json.dump(all_messages, f, ensure_ascii=False, indent=2)
    
    print(f"已将 {len(old_history)} 条旧消息合并到 {today_file}")
    
    # 备份旧文件
    os.rename(old_file, backup_file)
    print(f"旧文件已备份为 {backup_file}")
else:
    print("没有发现旧聊天记录文件")

print("处理完成！")
