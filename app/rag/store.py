"""
Chroma DB Store
벡터 DB 저장 및 검색
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.settings import CHROMA_PERSIST_DIR, EMBEDDING_MODEL
from typing import List, Dict
import uuid

class ChromaStore:
    """Chroma DB 래퍼"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name="lecture_materials",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
    
    def add_documents(self, documents: List[Dict]) -> int:
        """
        문서 추가
        
        Args:
            documents: [{"content": str, "metadata": dict}, ...]
        
        Returns:
            추가된 문서 개수
        """
        if not documents:
            return 0
        
        # Embedding 생성
        texts = [doc["content"] for doc in documents]
        embeddings = self.embedder.encode(texts).tolist()
        
        # ID 생성 (UUID로 충돌 방지)
        ids = [str(uuid.uuid4()) for _ in documents]
        
        # Metadata 준비
        metadatas = [doc.get("metadata", {}) for doc in documents]
        
        # Chroma에 추가
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        return len(documents)
    
    def search_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        문서 검색
        
        Args:
            query: 검색어
            top_k: 결과 개수
        
        Returns:
            [{"content": str, "metadata": dict, "distance": float}, ...]
        """
        # Query embedding
        query_embedding = self.embedder.encode([query]).tolist()
        
        # 검색
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        # 결과 포맷팅
        documents = []
        for i in range(len(results["ids"][0])):
            documents.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        
        return documents
    
    def clear(self):
        """모든 문서 삭제"""
        self.client.delete_collection("lecture_materials")
        self.collection = self.client.get_or_create_collection(
            name="lecture_materials",
            metadata={"hnsw:space": "cosine"}
        )