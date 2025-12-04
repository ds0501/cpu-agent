"""
OpenAI LLM Client
B파트 LangChain Runnable 인터페이스 제공
"""
from openai import OpenAI
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import Runnable
from app.config import OPENAI_API_KEY, MODEL_NAME
from typing import Dict, Any
import json

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)


class OpenAILLMRunnable(Runnable):
    """
    OpenAI LLM을 LangChain Runnable 인터페이스로 래핑
    B파트의 nodes.py에서 직접 사용 가능
    """
    def __init__(self, use_tools: bool = True):
        self.use_tools = use_tools
    
    def invoke(self, input: Dict[str, Any], config: Dict = None) -> AIMessage:
        """
        LangChain 스타일 invoke 메서드
        
        Args:
            input: {"messages": [HumanMessage, AIMessage, ...]}
            config: {"tools": [...]} (선택)
        
        Returns:
            AIMessage (content 또는 tool_calls 포함)
        """
        messages = input.get("messages", [])
        
        # LangChain 메시지를 OpenAI 포맷으로 변환
        openai_messages = self._convert_to_openai_format(messages)
        
        # System Prompt 자동 추가
        openai_messages = self._add_system_prompt(openai_messages)
        
        # Tool Spec 준비
        tools = None
        if self.use_tools and config and "tools" in config:
            tools = self._get_tool_specs()
        
        # OpenAI 호출
        response = self._call_openai(openai_messages, tools)
        
        # OpenAI 응답을 LangChain AIMessage로 변환
        return self._convert_to_langchain_format(response)
    
    def _convert_to_openai_format(self, messages):
        """LangChain 메시지 → OpenAI 포맷"""
        openai_messages = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                openai_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif isinstance(msg, AIMessage):
                # Tool calls가 있는 경우
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    tool_calls_openai = []
                    for tc in msg.tool_calls:
                        tool_calls_openai.append({
                            "id": tc.get("id"),
                            "type": "function",
                            "function": {
                                "name": tc.get("name"),
                                "arguments": json.dumps(tc.get("args"))
                            }
                        })
                    
                    openai_messages.append({
                        "role": "assistant",
                        "content": msg.content or "",
                        "tool_calls": tool_calls_openai
                    })
                else:
                    openai_messages.append({
                        "role": "assistant",
                        "content": msg.content or ""
                    })
            
            elif isinstance(msg, ToolMessage):
                openai_messages.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "name": msg.name,
                    "content": msg.content
                })
        
        return openai_messages
    
    def _add_system_prompt(self, messages):
        """System Prompt 자동 추가"""
        try:
            from app.config.prompts import SYSTEM_PROMPT
            system_content = SYSTEM_PROMPT
        except ImportError:
            system_content = "You are a helpful AI assistant."
        
        # 첫 메시지가 system이 아니면 추가
        if not messages or messages[0].get("role") != "system":
            messages = [
                {"role": "system", "content": system_content}
            ] + messages
        
        return messages
    
    def _get_tool_specs(self):
        """Tool Spec 가져오기"""
        try:
            from app.tools.registry import ALL_TOOL_SPECS
            return ALL_TOOL_SPECS
        except ImportError:
            return []
    
    def _call_openai(self, messages, tools):
        """OpenAI API 호출"""
        call_kwargs = {
            "model": MODEL_NAME,
            "messages": messages,
        }
        
        if tools:
            call_kwargs["tools"] = tools
            call_kwargs["tool_choice"] = "auto"
        
        try:
            response = client.chat.completions.create(**call_kwargs)
            return response
        except Exception as e:
            print(f"❌ LLM 호출 오류: {e}")
            raise
    
    def _convert_to_langchain_format(self, response):
        """OpenAI 응답 → LangChain AIMessage"""
        assistant_message = response.choices[0].message
        
        # Tool calls가 있으면
        if assistant_message.tool_calls:
            tool_calls = []
            for tc in assistant_message.tool_calls:
                tool_calls.append({
                    "name": tc.function.name,
                    "args": json.loads(tc.function.arguments),
                    "id": tc.id
                })
            
            return AIMessage(
                content=assistant_message.content or "",
                tool_calls=tool_calls
            )
        
        # 일반 답변
        return AIMessage(content=assistant_message.content or "")


# B파트에서 사용할 LLM 인스턴스
llm_with_tools = OpenAILLMRunnable(use_tools=True)
llm_for_reflection = OpenAILLMRunnable(use_tools=True)


# 호환성 함수 (직접 호출용)
def call_llm(messages: list, tools: list = None, **kwargs):
    """
    직접 OpenAI 호출 (비-LangChain 스타일)
    
    Args:
        messages: OpenAI 포맷 메시지
        tools: Tool spec 리스트
    
    Returns:
        OpenAI ChatCompletion 객체
    """
    # System Prompt 추가
    try:
        from app.config.prompts import SYSTEM_PROMPT
        if not messages or messages[0].get("role") != "system":
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + messages
    except ImportError:
        pass
    
    call_kwargs = {
        "model": MODEL_NAME,
        "messages": messages,
    }
    
    if tools:
        call_kwargs["tools"] = tools
        call_kwargs["tool_choice"] = "auto"
    
    call_kwargs.update(kwargs)
    
    try:
        response = client.chat.completions.create(**call_kwargs)
        return response
    except Exception as e:
        print(f"❌ LLM 호출 오류: {e}")
        raise