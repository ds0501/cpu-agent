"""
Tool Registry
모든 Tool을 중앙에서 관리
"""
from app.tools import calculator, time_tool, google_search, rag_tool, memory_tools

# Tool Spec 수집 (6개)
ALL_TOOL_SPECS = [
    calculator.TOOL_SPEC,
    time_tool.TOOL_SPEC,
    google_search.TOOL_SPEC,
    rag_tool.TOOL_SPEC,
    memory_tools.READ_MEMORY_TOOL_SPEC,
    memory_tools.WRITE_MEMORY_TOOL_SPEC,
]

TOOL_EXECUTORS = {
    "calculator": calculator.execute,
    "time_now": time_tool.execute,
    "google_search": google_search.execute,
    "rag_search": rag_tool.execute,
    "read_memory": memory_tools.execute_read_memory,
    "write_memory": memory_tools.execute_write_memory,
}


def execute_tool(tool_name: str, tool_args: dict) -> dict:
    """
    Tool 실행
    
    Args:
        tool_name: Tool 이름
        tool_args: Tool 인자
    
    Returns:
        {"success": bool, "result": any, "error": str}
    """
    executor = TOOL_EXECUTORS.get(tool_name)
    
    if not executor:
        return {
            "success": False,
            "result": None,
            "error": f"알 수 없는 tool: {tool_name}"
        }
    
    try:
        result = executor(**tool_args)
        return result
    
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "error": f"Tool 실행 오류: {str(e)}"
        }