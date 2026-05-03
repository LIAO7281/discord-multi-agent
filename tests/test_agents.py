"""
Tests for Discord Multi-Agent Support System
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.intent_agent import IntentAgent
from src.agents.reply_agent import ReplyAgent
from src.agents.quality_agent import QualityAgent


class TestIntentAgent(unittest.TestCase):
    """测试意图识别 Agent"""
    
    def setUp(self):
        """测试前准备"""
        self.agent = IntentAgent()
    
    def test_intent_types_defined(self):
        """测试意图类型是否正确定义"""
        expected_types = [
            "technical_support",
            "product_inquiry", 
            "community_rules",
            "billing",
            "feature_request",
            "bug_report",
            "general_chat",
            "human_handoff"
        ]
        for intent_type in expected_types:
            self.assertIn(intent_type, self.agent.intent_types)
    
    def test_human_handoff_detection(self):
        """测试人工转接关键词检测"""
        test_cases = [
            ("我想转人工", True),
            ("I want to speak to human", True),
            ("How to install?", False),
            ("产品多少钱", False)
        ]
        
        for message, expected in test_cases:
            result = self.agent.process({
                "message": message,
                "user_id": "test_user"
            })
            self.assertEqual(result["requires_human"], expected, 
                             f"Failed for message: {message}")
    
    @patch('src.agents.base_agent.BaseAgent._call_hermes')
    def test_process_returns_valid_structure(self, mock_call):
        """测试 process 返回正确的数据结构"""
        # Mock Hermes 返回
        mock_call.return_value = '{"intent": "general_chat", "confidence": 0.95, "language": "zh", "priority": "normal"}'
        
        result = self.agent.process({
            "message": "Hello",
            "user_id": "test_user"
        })
        
        # 验证返回结构
        self.assertIn("intent", result)
        self.assertIn("confidence", result)
        self.assertIn("language", result)
        self.assertIn("requires_human", result)
        self.assertIn("priority", result)
    
    def test_language_detection(self):
        """测试语言检测"""
        test_cases = [
            ("你好世界", "zh"),
            ("Hello World", "en"),
            ("こんにちは", "ja"),
            ("안녕하세요", "ko")
        ]
        
        for text, expected_lang in test_cases:
            result = self.agent._detect_language(text)
            self.assertEqual(result, expected_lang, 
                             f"Failed for text: {text}")


class TestReplyAgent(unittest.TestCase):
    """测试回复生成 Agent"""
    
    def setUp(self):
        """测试前准备"""
        self.agent = ReplyAgent()
    
    def test_prompt_templates_loaded(self):
        """测试提示词模板是否正确加载"""
        expected_intents = [
            "technical_support",
            "product_inquiry",
            "community_rules",
            "billing",
            "bug_report",
            "feature_request",
            "general_chat"
        ]
        
        for intent in expected_intents:
            self.assertIn(intent, self.agent.prompt_templates, 
                         f"Missing template for {intent}")
    
    @patch('src.agents.base_agent.BaseAgent._call_hermes')
    @patch('src.knowledge.rag_engine.RAGEngine.search')
    def test_process_returns_valid_structure(self, mock_search, mock_call):
        """测试 process 返回正确的数据结构"""
        # Mock RAG 搜索结果
        mock_search.return_value = [
            {"content": "Test content", "source": "test.md", "score": 0.9}
        ]
        
        # Mock Hermes 返回
        mock_call.return_value = "This is a test reply."
        
        result = self.agent.process({
            "message": "How to install?",
            "intent": {"intent": "technical_support", "language": "en"},
            "user_id": "test_user"
        })
        
        # 验证返回结构
        self.assertIn("reply", result)
        self.assertIn("sources", result)
        self.assertIn("confidence", result)
        self.assertIn("should_escalate", result)
    
    def test_should_escalate(self):
        """测试是否需要升级到人工"""
        test_cases = [
            ("I don't know how to fix this", True),
            ("The solution is...", False),
            ("不确定，建议联系人工", True),
            ("您可以尝试重启设备", False)
        ]
        
        for reply, expected in test_cases:
            result = self.agent._should_escalate(reply, "technical_support")
            self.assertEqual(result, expected, 
                             f"Failed for reply: {reply}")


class TestQualityAgent(unittest.TestCase):
    """测试质量审核 Agent"""
    
    def setUp(self):
        """测试前准备"""
        self.agent = QualityAgent()
    
    def test_community_guidelines_defined(self):
        """测试社区准则是否正确定义"""
        self.assertGreater(len(self.agent.community_guidelines), 0)
        self.assertIn("尊重", self.agent.community_guidelines)
    
    def test_quality_criteria_defined(self):
        """测试审核标准是否正确定义"""
        self.assertGreater(len(self.agent.quality_criteria), 0)
        self.assertIn("礼貌", self.agent.quality_criteria)
    
    @patch('src.agents.base_agent.BaseAgent._call_hermes')
    def test_process_returns_valid_structure(self, mock_call):
        """测试 process 返回正确的数据结构"""
        # Mock Hermes 返回
        mock_call.return_value = '{"approved": true, "score": 0.95, "issues": [], "rewritten_reply": "", "action": "send"}'
        
        result = self.agent.process({
            "original_message": "How to install?",
            "intent": {"intent": "technical_support"},
            "reply": "You can install by following this guide...",
            "user_id": "test_user"
        })
        
        # 验证返回结构
        self.assertIn("approved", result)
        self.assertIn("score", result)
        self.assertIn("issues", result)
        self.assertIn("final_reply", result)
        self.assertIn("action", result)
    
    def test_should_escalate_to_human(self):
        """测试是否需要转人工"""
        test_cases = [
            ({"action": "human", "score": 0.9}, True),
            ({"action": "send", "score": 0.9}, False),
            ({"action": "rewrite", "score": 0.5}, True),  # 低分
            ({"action": "send", "score": 0.3}, True),  # 低分
            ({"action": "send", "score": 0.9, "issues": ["a", "b", "c"]}, True),  # 多个问题
        ]
        
        for quality_result, expected in test_cases:
            result = self.agent.should_escalate_to_human(quality_result)
            self.assertEqual(result, expected, 
                             f"Failed for result: {quality_result}")


class TestAgentIntegration(unittest.TestCase):
    """测试 Agent 协作"""
    
    @patch('src.agents.base_agent.BaseAgent._call_hermes')
    @patch('src.knowledge.rag_engine.RAGEngine.search')
    def test_full_workflow(self, mock_search, mock_call):
        """测试完整工作流：意图识别 → 回复生成 → 质量审核"""
        # 1. Intent Agent
        intent_agent = IntentAgent()
        mock_call.return_value = '{"intent": "technical_support", "confidence": 0.95, "language": "zh", "priority": "normal"}'
        
        intent_result = intent_agent.process({
            "message": "安装失败怎么办？",
            "user_id": "test_user"
        })
        
        self.assertEqual(intent_result["intent"], "technical_support")
        
        # 2. Reply Agent
        reply_agent = ReplyAgent()
        mock_search.return_value = [
            {"content": "安装步骤...", "source": "install.md", "score": 0.9}
        ]
        mock_call.return_value = "您可以尝试以下步骤：1. 检查系统要求 2. 重新下载安装包..."
        
        reply_result = reply_agent.process({
            "message": "安装失败怎么办？",
            "intent": intent_result,
            "user_id": "test_user"
        })
        
        self.assertIn("reply", reply_result)
        
        # 3. Quality Agent
        quality_agent = QualityAgent()
        mock_call.return_value = '{"approved": true, "score": 0.95, "issues": [], "rewritten_reply": "", "action": "send"}'
        
        quality_result = quality_agent.process({
            "original_message": "安装失败怎么办？",
            "intent": intent_result,
            "reply": reply_result["reply"],
            "user_id": "test_user"
        })
        
        self.assertEqual(quality_result["action"], "send")
        self.assertGreater(quality_result["score"], 0.8)


if __name__ == '__main__':
    unittest.main()