from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable

class MockLLMRunnable(Runnable):
    """
    Tool Call이나 최종 답변을 임의로 반환하여 LangGraph 흐름을 테스트하기 위한 모의 LLM입니다.
    이 클래스는 반드시 AIMessage 객체를 반환해야 합니다.
    """
    def invoke(self, input, config=None):
        messages = input.get("messages", [])
        last_message = messages[-1]
        
        # 마지막 메시지가 Tool 실행 결과(ToolMessage)가 아니라 사용자 메시지(HumanMessage)인지 확인
        if isinstance(last_message, HumanMessage):
            last_human_message = last_message.content
        else:
            # Tool 실행 결과 메시지인 경우, 즉시 최종 답변으로 넘어가게 합니다.
            # 이 경우, Tool Call 조건을 통과하지 않고 아래 '최종 답변 모킹'으로 이동
            last_human_message = "" 
        
        # 1. Tool Call 유도 테스트 (예: '계산' 포함)
        if "계산" in last_human_message:
            print(">>> MOCK: Tool Call 반환 (calculator)")
            return AIMessage(
                content="", 
                tool_calls=[{
                    "name": "calculator",
                    "args": {"expression": "123 + 456"},
                    "id": "call_123"
                }]
            )
        
        # 2. Reflection Tool Call 유도 테스트 (Reflection LLM용)
        # config에 'tools' 인자가 없거나, 'llm_for_reflection'을 사용하는 경우로 가정
        if config is None or "tools" not in config:
            # Memory Tool 호출 모킹
            print(">>> MOCK REFLECTION: write_memory Tool Call 반환")
            return AIMessage(
                content="", 
                tool_calls=[{
                    "name": "write_memory",
                    "args": {"summary": "사용자가 계산 문제를 해결하는 법을 배웠음."},
                    "id": "call_456"
                }]
            )

        # 3. 최종 답변 모킹
        print(">>> MOCK: 최종 답변 반환")
        # Tool 결과가 State에 있다면, 그 결과가 반영되었다고 가정하고 답변합니다.
        return AIMessage(content="✅ **성공적으로 Tool을 사용하여 답변을 생성했습니다.** (Mock Tool 결과 반영됨)")
# B 역할의 nodes.py에서 사용할 LLM 객체
llm_with_tools = MockLLMRunnable()
llm_for_reflection = MockLLMRunnable()