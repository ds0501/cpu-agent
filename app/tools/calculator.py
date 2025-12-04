"""
계산기 Tool
수학 표현식 계산
"""

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "수학 계산을 수행합니다. 사칙연산, 제곱, 제곱근 등을 지원합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "계산할 수학 표현식 (예: '2+2', '10*5', 'sqrt(16)')"
                }
            },
            "required": ["expression"]
        }
    }
}


def execute(expression: str) -> dict:
    """
    계산 실행
    
    Args:
        expression: 수학 표현식
    
    Returns:
        {"success": bool, "result": str, "error": str}
    """
    import math
    
    # 안전한 eval을 위한 화이트리스트
    safe_dict = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "sqrt": math.sqrt,
        "pow": pow,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "exp": math.exp,
        "pi": math.pi,
        "e": math.e,
    }
    
    try:
        # 위험한 함수 제거
        expression = expression.replace("__", "").replace("import", "")
        
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        
        return {
            "success": True,
            "result": str(result),
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "error": f"계산 오류: {str(e)}"
        }