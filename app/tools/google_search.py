"""
Google Search Tool (Mock Version)
실제 API 없이 Tool Calling 기능 시연용
"""

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "google_search",
        "description": "웹에서 정보를 검색합니다. 최신 뉴스, 날씨, 일반 상식 등을 찾을 때 사용하세요.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색어"
                },
                "num_results": {
                    "type": "integer",
                    "description": "반환할 결과 개수 (기본값: 3)",
                    "default": 3
                }
            },
            "required": ["query"]
        }
    }
}


def execute(query: str, num_results: int = 3) -> dict:
    """
    Mock Google 검색
    
    실제 프로덕션에서는 Google Custom Search API나
    다른 검색 API를 연동할 수 있습니다.
    """
    # Mock 검색 결과
    mock_results = [
        {
            "title": f"{query} - 최신 정보",
            "link": "https://example.com/result1",
            "snippet": f"{query}에 대한 최신 정보입니다. (Mock 데이터)"
        },
        {
            "title": f"{query} 상세 가이드",
            "link": "https://example.com/result2", 
            "snippet": f"{query}의 상세한 설명과 예시를 제공합니다. (Mock 데이터)"
        },
        {
            "title": f"{query} 관련 뉴스",
            "link": "https://example.com/result3",
            "snippet": f"{query}에 대한 최근 뉴스와 트렌드입니다. (Mock 데이터)"
        }
    ]
    
    return {
        "success": True,
        "result": mock_results[:num_results],
        "error": None
    }