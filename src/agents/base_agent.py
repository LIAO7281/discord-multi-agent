"""
Base Agent Class - 所有 Agent 的基类
提供共用的 Hermes Agent 调用接口
"""

import os
import json
from typing import Dict, Any, Optional
import requests


class BaseAgent:
    """Agent 基类，封装 Hermes Agent 调用逻辑"""
    
    def __init__(self, agent_name: str, model: str = None, temperature: float = 0.7):
        """
        初始化 Agent
        
        Args:
            agent_name: Agent 名称（用于日志标识）
            model: 使用的模型（默认从环境变量读取）
            temperature: 温度参数（控制随机性）
        """
        self.agent_name = agent_name
        self.model = model or os.getenv("HERMES_MODEL", "deepseek-chat")
        self.temperature = temperature
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
        
    def _call_hermes(self, prompt: str, system_prompt: str = None, 
                      max_tokens: int = 1000) -> str:
        """
        调用 Hermes Agent (通过 OpenAI 兼容接口)
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词（定义 Agent 角色）
            max_tokens: 最大生成 token 数
            
        Returns:
            str: Agent 的回复内容
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[{self.agent_name}] Error calling Hermes: {e}")
            return ""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理输入的抽象方法（子类必须实现）
        
        Args:
            input_data: 输入数据字典
            
        Returns:
            Dict: 处理结果
        """
        raise NotImplementedError("Subclasses must implement process()")
    
    def log(self, message: str):
        """打印带 Agent 名称的日志"""
        print(f"[{self.agent_name}] {message}")