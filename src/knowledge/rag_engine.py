"""
RAG Engine - 检索增强生成引擎
用于从知识库中检索相关文档
"""

import os
import json
from typing import List, Dict
import numpy as np


class RAGEngine:
    """简化版 RAG 引擎（可替换为专业向量数据库）"""
    
    def __init__(self, knowledge_base_path: str = None):
        """
        初始化 RAG 引擎
        
        Args:
            knowledge_base_path: 知识库路径（存放 .txt/.md 文件）
        """
        self.knowledge_base_path = knowledge_base_path or "./knowledge_base"
        self.documents = []  # 存储文档 {content, source, embedding}
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        
        # 加载知识库
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """加载知识库文档（支持 .txt, .md）"""
        if not os.path.exists(self.knowledge_base_path):
            os.makedirs(self.knowledge_base_path, exist_ok=True)
            # 创建示例知识文档
            self._create_sample_knowledge()
            return
        
        print(f"[RAG] 加载知识库: {self.knowledge_base_path}")
        
        for filename in os.listdir(self.knowledge_base_path):
            if filename.endswith(('.txt', '.md')):
                filepath = os.path.join(self.knowledge_base_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.documents.append({
                            "content": content,
                            "source": filename,
                            "embedding": None  # 可后续添加向量嵌入
                        })
                except Exception as e:
                    print(f"[RAG] 加载文件失败 {filename}: {e}")
        
        print(f"[RAG] 已加载 {len(self.documents)} 个文档")
    
    def _create_sample_knowledge(self):
        """创建示例知识库文档"""
        samples = {
            "faq.md": """# 常见问题 FAQ

## 技术支持
Q: 如何安装？
A: 请参考文档 https://docs.example.com/install

Q: 运行报错怎么办？
A: 请查看日志文件，并联系技术支持。

## 产品咨询
Q: 有哪些订阅计划？
A: 我们提供免费版、专业版（¥99/月）、企业版（联系销售）

Q: 支持哪些平台？
A: Windows, macOS, Linux, iOS, Android

## 社区规则
Q: 可以发广告吗？
A: 不可以，违反者将被禁言。

Q: 如何成为版主？
A: 需要贡献 100+ 高质量回复，并申请。
""",
            "community_guidelines.md": """# 社区准则

## 基本规则
1. 保持尊重和友善
2. 禁止仇恨言论、歧视、骚扰
3. 禁止色情、暴力、非法内容
4. 禁止垃圾信息、过度刷屏
5. 保护隐私，不泄露个人信息

## 处罚措施
- 首次违规：警告
- 二次违规：禁言 24 小时
- 严重违规：永久封禁

## 举报方式
使用 Discord 内置举报功能，或联系管理员。
"""
        }
        
        for filename, content in samples.items():
            filepath = os.path.join(self.knowledge_base_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # 重新加载
        self._load_knowledge_base()
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        搜索相关文档（简化版：基于关键词匹配，可替换为向量检索）
        
        Args:
            query: 搜索查询
            top_k: 返回最相关的 k 个结果
            
        Returns:
            List[Dict]: [{"content": "...", "source": "..."}, ...]
        """
        if not self.documents:
            return []
        
        # 简化版：关键词匹配 + TF-IDF 相似度
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scores = []
        for doc in self.documents:
            content_lower = doc["content"].lower()
            content_words = set(content_lower.split())
            
            # 计算 Jaccard 相似度
            intersection = len(query_words & content_words)
            union = len(query_words | content_words)
            similarity = intersection / union if union > 0 else 0
            
            scores.append((similarity, doc))
        
        # 排序并返回 top_k
        scores.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in scores[:top_k]:
            if score > 0:  # 只返回有匹配的
                results.append({
                    "content": doc["content"][:500],  # 截断避免过长
                    "source": doc["source"],
                    "score": score
                })
        
        print(f"[RAG] 查询: '{query[:30]}...' 找到 {len(results)} 个相关文档")
        return results
    
    def add_document(self, content: str, source: str):
        """
        添加新文档到知识库
        
        Args:
            content: 文档内容
            source: 文档来源（文件名）
        """
        self.documents.append({
            "content": content,
            "source": source,
            "embedding": None
        })
        
        # 持久化到文件
        filepath = os.path.join(self.knowledge_base_path, source)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[RAG] 已添加文档: {source}")
