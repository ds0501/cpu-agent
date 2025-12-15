import json
from typing import Literal
from langchain_core.messages import ToolMessage
from app.graph.state import AgentState
from app.llm_client import llm_with_tools, llm_for_reflection # A 역할
from app.tools import run_tool # A 역할

# A 역할이 제공할 것으로 예상되는 Tool 이름 목록
AVAILABLE_TOOLS = ["google_search", "calculator", "time", "rag_search", "read_memory", "write_memory"]

def llm_node(state: AgentState) -> AgentState:
    """
    LLM을 호출하여 답변을 생성하거나 Tool 사용을 결정하는 노드 (Think).
    """
    print("--- LLM Node 실행 (Think) ---")
    messages = state["messages"]
    
    # 1. LLM 호출 (A 역할이 구현한 클라이언트 사용)
    # LangChain Runnable의 invoke 결과를 가져옴
    response = llm_with_tools.invoke(
        {"messages": messages},
        config={"tools": AVAILABLE_TOOLS}
    )
    
    # 2. 결과 처리
    # LLM 응답은 자동으로 State의 messages 리스트에 추가됩니다.
    return {"messages": [response]}

def tool_node(state: AgentState) -> AgentState:
    """
    Tool 호출을 실행하고 그 결과를 메시지로 State에 추가하는 노드 (Act & Observe).
    """
    print("--- Tool Node 실행 (Act & Observe) ---")
    messages = state["messages"]
    
    # 마지막 메시지에서 Tool Calls 추출
    last_message = messages[-1]
    if not last_message.tool_calls:
        print("경고: Tool Node에 진입했으나 Tool Call이 없습니다.")
        return state # Tool Call이 없으면 상태 변경 없이 반환

    # 추출된 Tool Calls 실행
    tool_results = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_call_id = tool_call["id"]
        
        print(f"Tool 호출: {tool_name} with args: {tool_args}")
        
        # 1. A 역할이 제공하는 run_tool 함수 호출 (핵심 협업 인터페이스)
        try:
            result_dict = run_tool(tool_name, tool_args)
            result = json.dumps(result_dict, ensure_ascii=False)
        except Exception as e:
            result = f"Error: Tool execution failed for {tool_name}. Details: {e}"
            print(result)

        # 2. ToolMessage 생성 및 결과 저장
        tool_results.append(
            ToolMessage(
                content=result,
                tool_call_id=tool_call_id,
                name=tool_name,
            )
        )
        
    # Tool 실행 결과 메시지를 State에 추가하여 LLM이 다음 턴에 볼 수 있게 함
    return {"messages": tool_results}


def reflection_node(state: AgentState) -> AgentState:
    """
    대화가 완료된 후, 장기 메모리 저장을 위해 Reflection을 수행하는 노드.
    이 노드에서 'write_memory' Tool을 호출하는 LLM을 사용합니다.
    """
    print("--- Reflection Node 실행 ---")
    messages = state["messages"]
    
    # 1. LLM 호출: 전체 대화 내용을 기반으로 저장할 메모리 요약을 생성하도록 요청 (A 역할 프롬프트 사용)
    # A 역할이 구현한 LLM 클라이언트 사용
    reflection_response = llm_for_reflection.invoke({"messages": messages})

    # 2. Tool Calls 확인 (Reflection LLM은 반드시 'write_memory' Tool을 호출해야 함)
    tool_calls = reflection_response.tool_calls
    
    if tool_calls and tool_calls[0]["name"] == "write_memory":
        tool_call = tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_call_id = tool_call["id"]
        
        print(f"Reflection Tool 호출: {tool_name} with args: {tool_args}")

        # 3. 'write_memory' Tool 실행
        try:
            result_dict = run_tool(tool_name, tool_args)
            result = json.dumps(result_dict, ensure_ascii=False)
        except Exception as e:
            result = f"Error: write_memory execution failed. Details: {e}"
            print(result)

        # Reflection 결과를 LLM에게 다시 전달할 필요는 없으므로,
        # 여기서는 상태에 ToolMessage를 추가하지 않고 로그만 남깁니다.
        # 성공적으로 실행되었다고 가정하고 다음 상태로 넘어갑니다.
        
    else:
        print("Reflection LLM이 'write_memory' Tool을 호출하지 않았습니다. 메모리 저장을 건너뜁니다.")

    # Reflection 후 상태 변경 없이 다음 단계 (Graph 종료)로 넘어갑니다.
    return state


def should_continue(state: AgentState) -> Literal["llm_node", "reflection_node", "end"]:
    """
    LangGraph의 조건부 Edge를 위한 함수. 다음 노드를 결정합니다.
    ReAct 구조: LLM 결과에 따라 Tool을 호출할지, 아니면 답변을 완료하고 종료할지 결정.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # 1. Tool Calls 확인: LLM이 Tool 사용을 요청했는지?
    if last_message.tool_calls:
        print("조건부 Edge: Tool Call 발견. Tool Node로 이동.")
        # Tool 사용을 요청했으면 tool_node로 이동하여 실행
        return "tool_node"
    
    # 2. 답변 완료 확인: 마지막 메시지가 Tool Call이 아니면 최종 답변으로 간주
    # 최종 답변을 생성했으면 대화 종료 후 Reflection 노드로 이동
    print("조건부 Edge: Tool Call 없음. 답변 완료. Reflection Node로 이동.")
    return "reflection_node"