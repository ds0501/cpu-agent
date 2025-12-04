"""
RAG Search Tool
Chroma DB에서 강의 자료 검색
"""

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "rag_search",
        "description": "색인된 강의 자료에서 관련 내용을 검색합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색할 내용"
                },
                "top_k": {
                    "type": "integer",
                    "description": "반환할 결과 개수 (기본값: 3)",
                    "default": 3
                }
            },
            "required": ["query"]
        }
    }
}


def execute(query: str, top_k: int = 3) -> dict:
    """
    RAG 검색 실행
    
    Args:
        query: 검색어
        top_k: 결과 개수
    
    Returns:
        {"success": bool, "result": list, "error": str}
    """
    try:
        from app.rag.store import ChromaStore
        
        store = ChromaStore()
        documents = store.search_documents(query, top_k=top_k)
        
        if not documents:
            return {
                "success": True,
                "result": "관련된 강의 자료가 없습니다. PDF 파일을 먼저 업로드해주세요.",
                "error": None
            }
        
        # 결과 포맷팅
        result_text = f"📚 '{query}'와 관련된 강의 내용:\n\n"
        for i, doc in enumerate(documents, 1):
            result_text += f"{i}. {doc['content'][:200]}...\n"
            result_text += f"   (출처: {doc['metadata'].get('source', 'Unknown')})\n\n"
        
        return {
            "success": True,
            "result": result_text,
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "error": f"RAG 검색 오류: {str(e)}"
        }