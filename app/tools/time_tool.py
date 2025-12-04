"""
Time Tool
현재 시간, 날짜 계산 등
"""
from datetime import datetime, timedelta

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "time_now",
        "description": "현재 시간을 조회하거나 날짜 계산을 수행합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["current", "add_days", "diff_days"],
                    "description": "수행할 작업 (current: 현재 시간, add_days: 날짜 더하기, diff_days: 날짜 차이)"
                },
                "days": {
                    "type": "integer",
                    "description": "더하거나 뺄 일수 (add_days에서 사용)"
                },
                "target_date": {
                    "type": "string",
                    "description": "대상 날짜 (YYYY-MM-DD 형식, diff_days에서 사용)"
                }
            },
            "required": ["action"]
        }
    }
}


def execute(action: str, days: int = None, target_date: str = None) -> dict:
    """
    시간 관련 작업 실행
    
    Args:
        action: 작업 종류 (current/add_days/diff_days)
        days: 더하거나 뺄 일수
        target_date: 대상 날짜 (YYYY-MM-DD)
    
    Returns:
        {"success": bool, "result": str, "error": str}
    """
    try:
        now = datetime.now()
        
        if action == "current":
            result = f"현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        
        elif action == "add_days":
            if days is None:
                return {
                    "success": False,
                    "result": None,
                    "error": "days 파라미터가 필요합니다"
                }
            
            future_date = now + timedelta(days=days)
            result = f"{days}일 후: {future_date.strftime('%Y-%m-%d %H:%M:%S')}"
        
        elif action == "diff_days":
            if target_date is None:
                return {
                    "success": False,
                    "result": None,
                    "error": "target_date 파라미터가 필요합니다"
                }
            
            target = datetime.strptime(target_date, "%Y-%m-%d")
            diff = (target - now).days
            result = f"{target_date}까지 {diff}일 남음"
        
        else:
            return {
                "success": False,
                "result": None,
                "error": f"알 수 없는 action: {action}"
            }
        
        return {
            "success": True,
            "result": result,
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "error": f"시간 계산 오류: {str(e)}"
        }