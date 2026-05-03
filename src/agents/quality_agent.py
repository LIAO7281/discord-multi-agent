"""
Quality Agent - 质量审核 Agent
检查回复是否符合社区规范，必要时重写或转人工
"""

from typing import Dict, Any
from src.agents.base_agent import BaseAgent


class QualityAgent(BaseAgent):
    """质量审核 Agent - 确保回复符合社区规范"""
    
    def __init__(self):
        super().__init__(
            agent_name="QualityAgent",
            temperature=0.2,  # 低温度，确保审核准确性
        )
        
        # 社区规范（可配置）
        self.community_guidelines = """社区准则：
1. 保持尊重和友善
2. 禁止仇恨言论、歧视、骚扰
3. 禁止色情、暴力、非法内容
4. 禁止垃圾信息、过度刷屏
5. 保护用户隐私，不泄露个人信息
6. 准确信息，不传播虚假信息
7. 遵守 Discord 服务条款"""

        # 审核标准
        self.quality_criteria = """审核标准：
1. 礼貌友好（评分 1-10）
2. 信息准确（无虚假信息）
3. 符合社区准则（无违规内容）
4. 语言适当（无冒犯性用语）
5. 有帮助性（真正解决用户问题）
6. 不过度推销（无过度营销）"""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        审核回复质量
        
        Args:
            input_data: {
                "original_message": "用户原始消息",
                "intent": {"intent": "类型", ...},
                "reply": "待审核的回复内容",
                "user_id": "用户ID",
                "history": [...]  # 对话历史
            }
            
        Returns:
            {
                "approved": True/False,  # 是否通过审核
                "score": 0.95,            # 质量评分 (0-1)
                "issues": ["issue1", ...],  # 发现的问题
                "final_reply": "最终回复内容",  # 可能重写
                "action": "send/rewrite/human"  # 建议操作
            }
        """
        original_message = input_data.get("original_message", "")
        intent = input_data.get("intent", {})
        reply = input_data.get("reply", "")
        intent_type = intent.get("intent", "general_chat")
        
        # 调用 Hermes Agent 进行审核
        system_prompt = f"""你是一个专业的社区客服质量审核专家。
审核客服回复是否符合规范，并返回 JSON 结果。

{self.quality_criteria}

返回严格 JSON 格式：
{{
  "approved": true/false,
  "score": 0.0-1.0,
  "issues": ["问题1", "问题2"],
  "rewritten_reply": "如果未通过，提供重写版本；如果通过，留空",
  "action": "send/rewrite/human"  // send=直接发送, rewrite=使用重写版本, human=转人工
}}

只返回 JSON，不要其他解释。"""

        prompt = f"""原始用户消息: {original_message}
问题类型: {intent_type}
待审核回复:
---
{reply}
---

请审核此回复。"""

        # 调用 Hermes Agent
        response = self._call_hermes(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1000
        )
        
        # 解析 JSON 响应
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # 确定最终回复
                final_reply = reply
                if not result.get("approved") and result.get("rewritten_reply"):
                    final_reply = result["rewritten_reply"]
                
                return {
                    "approved": result.get("approved", False),
                    "score": result.get("score", 0.0),
                    "issues": result.get("issues", []),
                    "final_reply": final_reply,
                    "action": result.get("action", "human")
                }
        except Exception as e:
            self.log(f"解析审核结果失败: {e}, 响应: {response}")
        
        # 默认：如果解析失败，转人工审核
        return {
            "approved": False,
            "score": 0.0,
            "issues": ["审核结果解析失败"],
            "final_reply": reply,
            "action": "human"
        }
    
    def should_escalate_to_human(self, quality_result: Dict[str, Any]) -> bool:
        """
        判断是否需要转人工
        
        Args:
            quality_result: 质量审核结果
            
        Returns:
            bool: 是否需要转人工
        """
        action = quality_result.get("action", "send")
        score = quality_result.get("score", 1.0)
        
        # 转人工条件
        if action == "human":
            return True
        if score < 0.6:  # 质量评分过低
            return True
        if len(quality_result.get("issues", [])) >= 3:  # 多个问题
            return True
            
        return False
