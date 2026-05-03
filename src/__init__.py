"""
Discord Multi-Agent Support System
基于 Hermes Agent 的多 Agent 协作 Discord 客服系统
"""

__version__ = "1.0.0"
__author__ = "AI Builder"

# 导入主要组件
from src.agents.intent_agent import IntentAgent
from src.agents.reply_agent import ReplyAgent
from src.agents.quality_agent import QualityAgent
from src.bot import DiscordBot

__all__ = [
    "IntentAgent",
    "ReplyAgent", 
    "QualityAgent",
    "DiscordBot"
]