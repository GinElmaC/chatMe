#!/usr/bin/env python3
"""数据迁移脚本：将旧的数据文件移动到新的子文件夹结构中"""

import os
import shutil
import json


def migrate_data():
    """迁移数据到新的文件夹结构"""
    config_path = "config.json"
    
    # 加载配置
    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    base_dir = config.get("data_dir", "data")
    subdirs = config.get("subdirectories", {})
    filenames = config.get("filenames", {})
    
    # 确保新的目录结构
    for subdir_name in subdirs.values():
        dir_path = os.path.join(base_dir, subdir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✅ 创建目录: {dir_path}")
    
    # 迁移文件
    files_to_migrate = [
        ("chat_history.json", "chat_history"),
        ("personality.json", "personality"),
        ("summarized_memory.json", "summarized_memory")
    ]
    
    for old_filename, subdir_key in files_to_migrate:
        old_path = os.path.join(base_dir, old_filename)
        if os.path.exists(old_path):
            subdir = subdirs.get(subdir_key, subdir_key)
            new_filename = filenames.get(subdir_key, old_filename)
            new_path = os.path.join(base_dir, subdir, new_filename)
            
            if not os.path.exists(new_path):
                shutil.move(old_path, new_path)
                print(f"✅ 迁移文件: {old_filename} -> {os.path.join(subdir, new_filename)}")
            else:
                print(f"⚠️  跳过: {old_filename} 已在目标位置")
        else:
            print(f"ℹ️  文件不存在: {old_filename}")
    
    print("\n✅ 数据迁移完成！")


if __name__ == "__main__":
    migrate_data()
