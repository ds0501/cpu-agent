from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.nodes import llm_node, tool_node, reflection_node, should_continue

def create_agent_graph():
    """
    Agent의 전체 ReAct + Reflection 파이프라인을 LangGraph로 정의하고 컴파일합니다.
    """
    # 1. StateGraph 초기화
    workflow = StateGraph(AgentState)
    
    # 2. Node 추가
    workflow.add_node("llm_node", llm_node)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("reflection_node", reflection_node)
    
    # 3. Entry Point 설정
    workflow.set_entry_point("llm_node")
    
    # 4. Edge 및 Conditional Edge 설계 (ReAct 루프 + Reflection)
    workflow.add_conditional_edges(
        "llm_node",
        should_continue,
        {
            "tool_node": "tool_node",
            "reflection_node": "reflection_node",
        },
    )

    workflow.add_edge("tool_node", "llm_node")
    workflow.add_edge("reflection_node", END)
    
    # 5. 그래프 컴파일
    app = workflow.compile()
    
    print("LangGraph Agent 파이프라인 컴파일 완료.")
    
    return app