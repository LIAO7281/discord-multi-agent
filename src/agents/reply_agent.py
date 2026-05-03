"""
Reply Agent - 专业回复 Agent
根据问题类型调用知识库，生成精准回复
"""

import os
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.knowledge.rag_engine import RAGEngine


class ReplyAgent(BaseAgent):
    """专业回复 Agent - 生成精准的客服回复"""
    
    def __init__(self):
        super().__init__(
            agent_name="ReplyAgent",
            temperature=0.7,  # 稍高温度，使回复更自然
        )
        # 初始化 RAG 引擎
        self.rag = RAGEngine()
        
        # 加载提示词模板
        self.prompt_templates = self._load_prompt_templates()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据意图生成回复
        
        Args:
            input_data: {
                "message": "用户消息",
                "intent": {"intent": "类型", "language": "zh", ...},
                "user_id": "用户ID",
                "channel_id": "频道ID",
                "history": [{"role": "user", "content": "..."}]  # 历史对话
            }
            
        Returns:
            {
                "reply": "生成的回复内容",
                "sources": ["知识库来源1", "来源2"],  # 引用的知识来源
                "confidence": 0.92,  # 回复置信度
                "should_escalate": False  # 是否需要升级到人工
            }
        """
        message = input_data.get("message", "")
        intent = input_data.get("intent", {})
        intent_type = intent.get("intent", "general_chat")
        language = intent.get("language", "en")
        history = input_data.get("history", [])
        
        # 1. 从知识库检索相关文档
        context_docs = self.rag.search(message, top_k=5)
        context_str = "\n\n".join([doc["content"] for doc in context_docs])
        sources = [doc["source"] for doc in context_docs]
        
        # 2. 根据意图类型选择提示词模板
        template = self.prompt_templates.get(intent_type, 
                                           self.prompt_templates["general_chat"])
        
        # 3. 构建完整提示词
        system_prompt = template.format(
            language=language,
            context=context_str if context_str else "暂无相关文档"
        )
        
        # 4. 构建对话历史
        history_str = ""
        for msg in history[-5:]:  # 只取最近 5 条
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_str += f"{role}: {content}\n"
        
        prompt = f"""用户消息: {message}

对话历史:
{history_str}

请生成专业、友好、简洁的回复。"""

        # 5. 调用 Hermes Agent
        reply = self._call_hermes(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000
        )
        
        # 6. 评估是否需要升级
        should_escalate = self._should_escalate(reply, intent_type)
        
        return {
            "reply": reply,
            "sources": list(set(sources)),  # 去重
            "confidence": 0.9 if context_docs else 0.6,
            "should_escalate": should_escalate
        }
    
    def _should_escalate(self, reply: str, intent_type: str) -> bool:
        """判断是否需要升级到人工"""
        # 简单规则：回复中包含不确定词汇
        uncertainty_keywords = [
            "不确定", "not sure", "不知道", "don't know",
            "无法回答", "cannot answer", "建议联系", "please contact"
        ]
        return any(kw in reply.lower() for kw in uncertainty_keywords)
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载各意图类型的提示词模板"""
        return {
            "technical_support": """你是一个技术支持专家，使用以下知识库内容回答用户的技术问题。
保持专业、准确，提供可执行的步骤。

语言: {language}
知识库内容:
{context}

回答规则:
1. 先确认问题理解
2. 提供分步解决方案
3. 如果涉及代码，提供完整示例
4. 如果无法解决，建议联系人工并提供参考链接""",
            
            "product_inquiry": """你是一个产品咨询专家，基于以下知识库回答用户的产品相关问题。
突出产品优势，但保持诚实，不夸大。

语言: {language}
知识库内容:
{context}

回答规则:
1. 直接回答用户问题
2. 适当介绍相关功能
3. 如有价格问题，提供准确信息
4. 引导用户尝试产品""",
            
            "community_rules": """你是一个社区管理专家，解释社区规则和最佳实践。
保持友好但坚定，确保用户理解规则。

语言: {language}
知识库内容:
{context}

回答规则:
1. 引用具体的规则条款
2. 解释规则的原因
3. 提供正确做法的示例
4. 对违规行为温和提醒""",
            
            "billing": """你是一个账单/支付支持专家。
处理订阅、退款、发票等问题，保持耐心和透明。

语言: {language}
知识库内容:
{context}

回答规则:
1. 确认用户的具体问题
2. 提供清晰的账单说明
3. 退款请求需要人工处理，但可以解释流程
4. 保护用户隐私，不询问敏感信息""",
            
            "bug_report": """你是一个 Bug 报告处理专家。
收集必要信息，确认问题，并告知处理流程。

语言: {language}

回答规则:
1. 感谢用户报告
2. 收集关键信息：复现步骤、环境、截图
3. 确认是否已记录
4. 告知预计处理时间""",
            
            "feature_request": """你是一个产品反馈专家。
认真听取功能建议，告知反馈流程。

语言: {language}

回答规则:
1. 感谢建议
2. 确认理解需求
3. 告知评估流程
4. 可以提供类似功能的替代方案""",
            
            "general_chat": """你是一个友好的社区助手。
进行自然对话，适当引导到有帮助的话题。

语言: {language}
知识库内容:
{context}

回答规则:
1. 保持友好和自然
2. 简要介绍社区资源
3. 如果话题转向技术支持/产品咨询，主动提供专业帮助
4. 不要过度推销"""
        }
