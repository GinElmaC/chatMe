import os
import sys
import gc
import psutil
from typing import Dict, Any, Optional


def get_memory_usage() -> Dict[str, float]:
    """获取当前进程的内存使用情况（MB）"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "rss": memory_info.rss / 1024 / 1024,  # 常驻内存
        "vms": memory_info.vms / 1024 / 1024,  # 虚拟内存
    }


def force_gc() -> Dict[str, Any]:
    """强制执行垃圾回收并返回统计信息"""
    gc.collect()
    
    stats = {}
    for generation in range(3):
        stats[f"gen_{generation}"] = gc.get_count()[generation]
    
    return {
        "collections": stats,
        "memory_after": get_memory_usage()
    }


def get_disk_usage(path: str = ".") -> Dict[str, float]:
    """获取指定路径的磁盘使用情况（MB）"""
    usage = psutil.disk_usage(path)
    return {
        "total": usage.total / 1024 / 1024,
        "used": usage.used / 1024 / 1024,
        "free": usage.free / 1024 / 1024,
        "percent": usage.percent
    }


class MemoryMonitor:
    """简单的内存监控器"""
    
    def __init__(self, log_interval: int = 60):
        self.log_interval = log_interval
        self.max_rss = 0.0
        self.history = []
    
    def check(self, label: str = "") -> Dict[str, Any]:
        """检查内存使用情况"""
        usage = get_memory_usage()
        
        if usage["rss"] > self.max_rss:
            self.max_rss = usage["rss"]
        
        self.history.append({
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "label": label,
            "rss": usage["rss"],
            "vms": usage["vms"]
        })
        
        return usage
    
    def force_gc_and_check(self, label: str = "") -> Dict[str, Any]:
        """强制执行GC并检查"""
        gc_result = force_gc()
        usage = self.check(label + " (after GC)")
        return {
            "gc_result": gc_result,
            "usage": usage
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "max_rss": self.max_rss,
            "check_count": len(self.history),
            "last_check": self.history[-1] if self.history else None
        }
