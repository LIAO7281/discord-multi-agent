"""
Utils Module - 工具函数
"""

import re
import logging


def setup_logging(level: str = "INFO"):
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def clean_discord_message(content: str) -> str:
    """
    清理 Discord 消息（去除提及、表情等）
    """
    # 去除用户提及 <@!123456789>
    content = re.sub(r'<@!?\d+>', '', content)
    # 去除频道提及 <#123456789>
    content = re.sub(r'<#\d+>', '', content)
    # 去除表情 <:emoji:123456789>
    content = re.sub(r'<:\w+:\d+>', '', content)
    # 去除自定义表情 <a:emoji:123456789>
    content = re.sub(r'<a:\w+:\d+>', '', content)
    # 去除 Markdown 格式（简单处理）
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # 粗体
    content = re.sub(r'\*(.*?)\*', r'\1', content)      # 斜体
    content = re.sub(r'__(.*?)__', r'\1', content)      # 下划线
    
    return content.strip()


def split_long_message(content: str, max_length: int = 2000) -> list:
    """
    将长消息分割成 Discord 允许的长度（2000字符）
    """
    if len(content) <= max_length:
        return [content]
    
    chunks = []
    while content:
        if len(content) <= max_length:
            chunks.append(content)
            break
        
        # 尝试在句子结束处分割
        split_point = content.rfind('. ', 0, max_length)
        if split_point == -1:
            split_point = content.rfind(' ', 0, max_length)
        if split_point == -1:
            split_point = max_length
        
        chunks.append(content[:split_point + 1])
        content = content[split_point + 1:]
    
    return chunks


def extract_urls(text: str) -> list:
    """提取文本中的 URL"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def is_bot_mentioned(message: str, bot_id: str) -> bool:
    """检查消息是否提及了 Bot"""
    return f'<@{bot_id}>' in message or f'<@!{bot_id}>' in message