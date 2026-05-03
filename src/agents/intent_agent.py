"""
Intent Agent - 意图识别 Agent
分析用户消息，分类问题类型
"""

from typing import Dict, Any
from src.agents.base_agent import BaseAgent


class IntentAgent(BaseAgent):
    """意图识别 Agent - 分析用户消息并确定问题类型"""
    
    def __init__(self):
        super().__init__(
            agent_name="IntentAgent",
            temperature=0.3,  # 低温度，提高分类准确性
        )
        
        # 定义支持的问题类型
        self.intent_types = [
            "technical_support",  # 技术支持
            "product_inquiry",    # 产品咨询
            "community_rules",     # 社区规则
            "billing",            # 账单/支付
            "feature_request",     # 功能请求
            "bug_report",         # Bug 报告
            "general_chat",       # 一般聊天
            "human_handoff"        # 需要转人工
        ]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析用户消息并返回意图分类
        
        Args:
            input_data: {
                "message": "用户消息内容",
                "user_id": "用户ID",
                "channel_id": "频道ID",
                "history": [{"role": "user", "content": "..."}]  # 可选历史
            }
            
        Returns:
            {
                "intent": "意图类型",
                "confidence": 0.95,  # 置信度
                "language": "zh",      # 检测到的语言
                "requires_human": False,  # 是否需要转人工
                "priority": "normal"   # 优先级: low/normal/high/urgent
            }
        """
        message = input_data.get("message", "")
        user_id = input_data.get("user_id", "unknown")
        
        # 检测是否需要转人工
        handoff_keywords = ["人工", "human", "转人工", "speak to human"]
        requires_human = any(kw in message.lower() for kw in handoff_keywords)
        
        if requires_human:
            return {
                "intent": "human_handoff",
                "confidence": 1.0,
                "language": self._detect_language(message),
                "requires_human": True,
                "priority": "high"
            }
        
        # 构建意图识别提示词
        system_prompt = """你是一个 Discord 社区客服意图识别专家。
分析用户消息，返回 JSON 格式的意图分类。

支持的意图类型：
- technical_support: 技术支持（安装、配置、报错等）
- product_inquiry: 产品咨询（功能、价格、使用等）
- community_rules: 社区规则（行为规范、处罚、权限等）
- billing: 账单/支付（订阅、退款、发票等）
- feature_request: 功能请求（建议、反馈等）
- bug_report: Bug 报告（崩溃、异常、错误等）
- general_chat: 一般聊天（问候、闲聊等）

返回严格 JSON 格式：
{
  "intent": "意图类型",
  "confidence": 0.0-1.0,
  "language": "zh/en/ja/ko 等",
  "priority": "low/normal/high/urgent"
}

只返回 JSON，不要其他解释。"""

        prompt = f"用户消息: {message}\n用户ID: {user_id}"
        
        # 调用 Hermes Agent
        response = self._call_hermes(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=500
        )
        
        # 解析 JSON 响应
        try:
            # 提取 JSON（可能夹带markdown代码块）
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result["requires_human"] = False
                return result
        except Exception as e:
            self.log(f"解析意图失败: {e}, 响应: {response}")
        
        # 默认返回一般聊天
        return {
            "intent": "general_chat",
            "confidence": 0.5,
            "language": self._detect_language(message),
            "requires_human": False,
            "priority": "normal"
        }
    
    def _detect_language(self, text: str) -> str:
        """简单语言检测（可替换为专业库如 langdetect）"""
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return "zh"
        elif any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):
            return "ja"
        elif any('\uac00' <= char <= '\ud7af' for char in text):
            return "ko"
        else:
            return "en"
