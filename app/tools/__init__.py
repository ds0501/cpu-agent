"""
Tools Module
B파트와의 통합 인터페이스
"""

# A파트 Tool Registry export
from app.tools.registry import execute_tool, ALL_TOOL_SPECS

# B파트 호환 함수들
def run_tool(tool_name: str, tool_args: dict) -> dict:
    """
    B파트 호환용 tool 실행 함수
    app.tools.run_tool로 import 가능
    """
    result = execute_tool(tool_name, tool_args)
    
    # B파트가 기대하는 형식으로 변환
    if result.get("success"):
        return {
            "result": result.get("result"),
            "error": None
        }
    else:
        return {
            "result": None,
            "error": result.get("error")
        }


def index_pdf_file(file_path: str) -> bool:
    """
    B파트 호환용 PDF 색인 함수
    app.tools.index_pdf_file로 import 가능
    """
    try:
        from app.rag.indexer import PDFIndexer
        
        indexer = PDFIndexer()
        chunks = indexer.index_pdf(file_path)
        
        return chunks > 0
    
    except Exception as e:
        print(f"❌ PDF 색인 오류: {e}")
        return False


# B파트에서 사용할 export
__all__ = [
    "run_tool",
    "index_pdf_file",
    "execute_tool",
    "ALL_TOOL_SPECS"
]