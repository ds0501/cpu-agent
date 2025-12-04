"""
시간 Tool
현재 시간, 날짜 계산
"""
from datetime import datetime, timedelta

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "현재 시간과 날짜를 반환하거나, 날짜 계산을 수행합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["current", "add_days", "diff_days"],
                    "description": "수행할 작업: current(현재 시간), add_days(날짜 더하기), diff_days(날짜 차이 계산)"
                },
                "days": {
                    "type": "integer",
                    "description": "더하거나 뺄 일수 (add_days에서 사용)"
                },
                "target_date": {
                    "type": "string",
                    "description": "목표 날짜 (YYYY-MM-DD 형식, diff_days에서 사용)"
                }
            },
            "required": ["action"]
        }
    }
}


def execute(action: str, days: int = 0, target_date: str = None) -> dict:
    """
    시간 관련 작업 실행
    
    Args:
        action: 작업 종류
        days: 일수
        target_date: 목표 날짜
    
    Returns:
        {"success": bool, "result": str, "error": str}
    """
    try:
        now = datetime.now()
        
        if action == "current":
            result = now.strftime("%Y-%m-%d %H:%M:%S")
            return {
                "success": True,
                "result": f"현재 시간: {result}",
                "error": None
            }
        
        elif action == "add_days":
            target = now + timedelta(days=days)
            result = target.strftime("%Y-%m-%d")
            return {
                "success": True,
                "result": f"{days}일 후: {result}",
                "error": None
            }
        
        elif action == "diff_days":
            if not target_date:
                raise ValueError("target_date가 필요합니다")
            
            target = datetime.strptime(target_date, "%Y-%m-%d")
            diff = (target - now).days
            
            return {
                "success": True,
                "result": f"{target_date}까지 {diff}일 남음",
                "error": None
            }
        
        else:
            raise ValueError(f"알 수 없는 action: {action}")
    
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "error": f"시간 계산 오류: {str(e)}"
        }