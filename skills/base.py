
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseSkill(ABC):
    """技能基类"""
    
    name: str = "base_skill"
    description: str = "基础技能"
    version: str = "1.0.0"
    
    # 解锁该技能所需的关系等级 (0-4)
    unlock_level: int = 0
    
    def __init__(self, memory_manager, llm_client):
        """
        初始化技能
        
        Args:
            memory_manager: MemoryManager 实例
            llm_client: LLMClient 实例
        """
        self.memory = memory_manager
        self.llm = llm_client
    
    @abstractmethod
    def can_handle(self, message: str) -> bool:
        """
        判断该技能是否能处理用户消息
        
        Args:
            message: 用户输入的消息
            
        Returns:
            bool: 是否能处理
        """
        pass
    
    @abstractmethod
    def execute(self, message: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        执行技能，返回结构化数据
        
        Args:
            message: 用户输入的消息
            context: 上下文信息
            
        Returns:
            Optional[Dict[str, Any]]: 技能返回的数据，None 表示不处理
        """
        pass
    
    def is_available(self) -> bool:
        """
        检查技能是否可用（根据关系等级等）
        
        Returns:
            bool: 是否可用
        """
        try:
            current_level = self.memory.get_relationship_level()
            return current_level >= self.unlock_level
        except Exception:
            return True

