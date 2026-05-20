
from .base import BaseSkill
from .datetime_skill import DateTimeSkill

# 注册所有可用技能
SKILLS = [
    DateTimeSkill,
    # 添加更多技能...
]

__all__ = ['SKILLS', 'BaseSkill']
