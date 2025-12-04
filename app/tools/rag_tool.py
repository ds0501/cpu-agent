"""
RAG Search Tool
강의 자료 검색
"""

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "search_lectures",
        "description": "강의 자료(PDF)에서 관련 내용을 검색합니다. 수업 내용, 슬라이드 내용 등을 찾을 때 사용하세요.",
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
    강의 자료 검색
    
    Args:
        query: 검색어
        top_k: 결과 개수
    
    Returns:
        {"success": bool, "result": list, "error": str}
    """
    try:
        from app.rag.store import ChromaStore
        
        store = ChromaStore()
        results = store.search_documents(query, top_k=top_k)
        
        if not results:
            return {
                "success": True,
                "result": [],
                "error": "검색 결과가 없습니다. PDF 파일을 먼저 업로드하세요."
            }
        
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc["content"],
                "metadata": doc["metadata"],
                "similarity": doc.get("distance", 0)
            })
        
        return {
            "success": True,
            "result": formatted_results,
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "error": f"RAG 검색 오류: {str(e)}"
        }