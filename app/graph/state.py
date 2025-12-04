from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import AnyMessage # AnyMessage 가져오기 경로 수정
from langgraph.graph.message import add_messages 

# Agent의 상태를 정의하는 TypedDict
# 모든 노드가 이 상태 객체를 읽고 업데이트합니다.
class AgentState(TypedDict):
    """
    LangGraph 에이전트의 상태를 정의합니다.
    - messages: 채팅 히스토리 및 Tool 호출/결과를 포함하는 메시지 리스트 (단기 메모리 역할)
    - lecture_index_status: 강의 자료 색인 상태 (예: 'READY', 'PENDING')
    - long_term_memory_query: Reflection 노드에서 장기 메모리 저장에 사용할 쿼리 (선택 사항)
    """
    messages: Annotated[List[AnyMessage], add_messages]
    lecture_index_status: str
    long_term_memory_query: str

# LangGraph의 State는 messages 리스트를 자동으로 append 하도록 설정됩니다..