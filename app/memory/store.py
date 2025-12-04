"""
Long-term Memory Store
Chroma DB를 사용한 장기 메모리 저장
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.settings import CHROMA_PERSIST_DIR, EMBEDDING_MODEL
from typing import List, Dict
from datetime import datetime
import json
import uuid

class MemoryStore:
    """장기 메모리 저장소"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name="long_term_memory",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
    
    def add_memory(self, content: str, metadata: dict = None) -> str:
        """
        메모리 추가
        
        Args:
            content: 저장할 내용
            metadata: 메타데이터 (timestamp, tags 등)
        
        Returns:
            메모리 ID
        """
        # Timestamp 자동 추가
        if metadata is None:
            metadata = {}
        
        metadata["timestamp"] = datetime.now().isoformat()
        
        # Embedding 생성
        embedding = self.embedder.encode([content]).tolist()[0]
        
        # ID 생성 (UUID 사용)
        memory_id = str(uuid.uuid4())
        
        # Chroma에 저장
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )
        
        return memory_id
    
    def search_memory(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        메모리 검색
        
        Args:
            query: 검색어
            top_k: 결과 개수
        
        Returns:
            관련 메모리 리스트
        """
        # Query embedding
        query_embedding = self.embedder.encode([query]).tolist()
        
        # 검색
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        # 결과 포맷팅
        memories = []
        for i in range(len(results["ids"][0])):
            memories.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "similarity": 1 - results["distances"][0][i]  # cosine similarity
            })
        
        return memories
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        """
        최근 메모리 가져오기
        
        Args:
            limit: 개수
        
        Returns:
            최근 메모리 리스트
        """
        # Chroma의 모든 데이터 가져오기
        all_data = self.collection.get()
        
        if not all_data["ids"]:
            return []
        
        # Timestamp로 정렬
        memories = []
        for i in range(len(all_data["ids"])):
            memories.append({
                "id": all_data["ids"][i],
                "content": all_data["documents"][i],
                "metadata": all_data["metadatas"][i]
            })
        
        # Timestamp 기준 내림차순 정렬
        memories.sort(
            key=lambda x: x["metadata"].get("timestamp", ""),
            reverse=True
        )
        
        return memories[:limit]
    
    def clear_all(self):
        """모든 메모리 삭제"""
        self.client.delete_collection("long_term_memory")
        self.collection = self.client.get_or_create_collection(
            name="long_term_memory",
            metadata={"hnsw:space": "cosine"}
        )