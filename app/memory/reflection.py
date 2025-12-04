"""
Memory Reflection
대화 내용을 분석하여 중요한 정보 추출
"""
from app.memory.store import MemoryStore
from typing import List, Dict

class MemoryReflection:
    """메모리 반영 시스템"""
    
    def __init__(self):
        self.store = MemoryStore()
    
    def reflect_and_save(self, summary: str, tags: List[str] = None) -> str:
        """
        Reflection 결과 저장
        
        Args:
            summary: LLM이 생성한 대화 요약
            tags: 태그 리스트 (예: ["학습", "약점", "선호도"])
        
        Returns:
            저장된 메모리 ID
        """
        metadata = {}
        
        if tags:
            metadata["tags"] = tags
        
        memory_id = self.store.add_memory(summary, metadata)
        
        print(f"💾 Reflection 저장 완료: {memory_id}")
        print(f"   내용: {summary}")
        
        return memory_id
    
    def get_relevant_context(self, query: str, top_k: int = 3) -> str:
        """
        현재 질문과 관련된 과거 메모리 가져오기
        
        Args:
            query: 현재 질문
            top_k: 가져올 메모리 개수
        
        Returns:
            관련 메모리를 텍스트로 포맷팅
        """
        memories = self.store.search_memory(query, top_k=top_k)
        
        if not memories:
            return "관련된 과거 기록이 없습니다."
        
        context = "📚 과거 학습 기록:\n"
        for i, mem in enumerate(memories, 1):
            context += f"{i}. {mem['content']}\n"
        
        return context