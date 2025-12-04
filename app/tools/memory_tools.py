"""
Memory Tools
read_memory, write_memory Tool 구현
"""

# Read Memory Tool Spec
READ_MEMORY_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "read_memory",
        "description": "사용자의 과거 학습 패턴, 선호도, 약점 등을 검색합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색할 내용 (예: '사용자가 어려워하는 주제', '지난주 학습 내용')"
                },
                "top_k": {
                    "type": "integer",
                    "description": "반환할 메모리 개수 (기본값: 3)",
                    "default": 3
                }
            },
            "required": ["query"]
        }
    }
}

# Write Memory Tool Spec
WRITE_MEMORY_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "write_memory",
        "description": "중요한 학습 내용이나 사용자 특성을 장기 메모리에 저장합니다. Reflection 노드에서 자동 호출됩니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "저장할 내용 요약"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "태그 (예: ['학습', '약점', '선호도'])",
                    "default": []
                }
            },
            "required": ["summary"]
        }
    }
}


def execute_read_memory(query: str, top_k: int = 3) -> dict:
    """
    메모리 읽기 실행
    """
    try:
        from app.memory.store import MemoryStore
        
        store = MemoryStore()
        memories = store.search_memory(query, top_k=top_k)
        
        if not memories:
            return {
                "success": True,
                "result": "관련된 과거 기록이 없습니다.",
                "error": None
            }
        
        # 결과 포맷팅
        result_text = f"📚 '{query}'와 관련된 과거 기록:\n\n"
        for i, mem in enumerate(memories, 1):
            result_text += f"{i}. {mem['content']}\n"
            result_text += f"   (저장 시간: {mem['metadata'].get('timestamp', 'N/A')})\n\n"
        
        return {
            "success": True,
            "result": result_text,
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "error": f"메모리 읽기 오류: {str(e)}"
        }


def execute_write_memory(summary: str, tags: list = None) -> dict:
    """
    메모리 쓰기 실행
    """
    try:
        from app.memory.reflection import MemoryReflection
        
        reflection = MemoryReflection()
        memory_id = reflection.reflect_and_save(summary, tags)
        
        return {
            "success": True,
            "result": f"메모리 저장 완료 (ID: {memory_id})",
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "error": f"메모리 저장 오류: {str(e)}"
        }