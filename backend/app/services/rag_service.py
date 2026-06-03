"""
RAG 知识库服务 —— 文档分块、向量化、语义检索。

开发模式：使用 sentence-transformers 本地模型（无需外部 API）。
生产模式：可切换 OpenAI / DeepSeek Embedding API。
"""

import hashlib
import json
import uuid
from typing import Optional

import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.utils.api_client import MODEL_NAME, _get_client


class RAGService:
    """知识库 RAG 服务 —— 管理文档分块和语义检索。"""

    def __init__(self):
        self.chunks: list[dict] = []  # 内存存储（开发模式）
        self.embeddings: Optional[np.ndarray] = None
        self._embedding_model = None

    def _get_embedding_model(self):
        """延迟加载嵌入模型。Vercel 环境降级为简单嵌入。"""
        if self._embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer(
                    "all-MiniLM-L6-v2"
                )
            except ImportError:
                self._embedding_model = "llm"
        return self._embedding_model

    def _compute_embedding(self, text: str) -> list[float]:
        """计算文本的嵌入向量。"""
        model = self._get_embedding_model()

        if model == "llm":
            # 降级方案：用 LLM 生成关键词向量（简单 TF 权重）
            return self._simple_embed(text)
        else:
            # 使用 sentence-transformers
            embedding = model.encode([text], normalize_embeddings=True)
            return embedding[0].tolist()

    def _simple_embed(self, text: str) -> list[float]:
        """简单词汇重叠嵌入（降级方案，开发调试用）。"""
        # 分词并计算字符级 n-gram 哈希作为简单特征
        words = text.lower().split()
        # 使用 384 维（与 all-MiniLM-L6-v2 一致）
        vec = np.zeros(384)
        for i, word in enumerate(words):
            h = hash(word) % 384
            vec[h] += 1.0
        # 归一化
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def add_document(
        self,
        filename: str,
        content: str,
        file_type: str,
    ) -> str:
        """
        添加文档到知识库。

        流程：分块 → 嵌入 → 存入内存向量库

        返回：document_id
        """
        doc_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        # 分块
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.rag_chunk_size,
            chunk_overlap=settings.rag_chunk_overlap,
            separators=["\n\n", "\n", "。", ".", " ", ""],
        )
        chunk_texts = splitter.split_text(content)

        # 为每个块生成嵌入
        for i, chunk_text in enumerate(chunk_texts):
            embedding = self._compute_embedding(chunk_text)
            self.chunks.append({
                "id": str(uuid.uuid4()),
                "document_id": doc_id,
                "chunk_index": i,
                "content": chunk_text,
                "embedding": embedding,
                "filename": filename,
            })

        # 更新嵌入矩阵
        if self.chunks:
            self.embeddings = np.array([c["embedding"] for c in self.chunks])

        return doc_id

    def search(
        self,
        query: str,
        top_k: int = None,
        threshold: float = None,
    ) -> list[dict]:
        """
        语义搜索知识库。

        参数：
            query: 查询文本
            top_k: 返回结果数（默认从配置读取）
            threshold: 相似度阈值（默认从配置读取）

        返回：[{content, score, filename}, ...]
        """
        if not self.chunks:
            return []

        top_k = top_k or settings.rag_top_k
        threshold = threshold or settings.rag_similarity_threshold

        # 计算查询嵌入
        query_embedding = np.array(self._compute_embedding(query))

        # 余弦相似度
        similarities = np.dot(self.embeddings, query_embedding)

        # 排序取 TopK
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= threshold:
                results.append({
                    "content": self.chunks[idx]["content"],
                    "score": score,
                    "filename": self.chunks[idx].get("filename", ""),
                    "chunk_index": self.chunks[idx]["chunk_index"],
                })

        return results

    def get_stats(self) -> dict:
        """返回知识库统计信息。"""
        return {
            "total_chunks": len(self.chunks),
            "total_documents": len(set(c["document_id"] for c in self.chunks)),
        }

    def delete_document(self, document_id: str) -> int:
        """删除文档及其所有分块。返回删除的分块数。"""
        before = len(self.chunks)
        self.chunks = [
            c for c in self.chunks if c["document_id"] != document_id
        ]
        after = len(self.chunks)
        if self.chunks:
            self.embeddings = np.array([c["embedding"] for c in self.chunks])
        else:
            self.embeddings = None
        return before - after

    def list_documents(self) -> list[dict]:
        """返回所有文档信息（去重）。"""
        seen = {}
        for chunk in self.chunks:
            doc_id = chunk["document_id"]
            if doc_id not in seen:
                seen[doc_id] = {
                    "document_id": doc_id,
                    "filename": chunk.get("filename", ""),
                    "chunk_count": 0,
                }
            seen[doc_id]["chunk_count"] += 1
        return list(seen.values())


# 全局单例
rag_service = RAGService()
