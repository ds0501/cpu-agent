import gradio as gr
from typing import List, Tuple
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from app.graph.app import create_agent_graph
from app.graph.state import AgentState 
from app.tools import index_pdf_file
import asyncio

# 에이전트 그래프를 한 번만 초기화하는 전역 변수 (지연 초기화)
_agent_app = None

def get_agent_app():
    """에이전트 그래프를 초기화하고 반환합니다."""
    global _agent_app
    if _agent_app is None:
        _agent_app = create_agent_graph()
    return _agent_app


# LangGraph 실행 및 채팅 기록 관리 함수
async def run_agent(message: str, history: List[Tuple[str, str]]):
    """
    사용자 메시지를 받아 LangGraph Agent를 실행하고 결과를 반환합니다.
    """
    agent_app = get_agent_app()
    chat_history = []
    # Gradio history의 튜플 메시지를 LangChain 메시지 객체로 변환
    for item in history:
        user_msg = None
        ai_msg = None
        
        # 1. 항목이 튜플(이전 방식)인 경우 처리
        if isinstance(item, tuple) and len(item) == 2:
            user_msg, ai_msg = item
            
        # 2. 항목이 딕셔너리(Gradio ChatMessage)인 경우 처리 (주로 발생하는 문제)
        elif isinstance(item, dict):
            # 'content'가 리스트이고 딕셔너리를 포함하는지 확인하여 텍스트 추출
            if item.get('role') == 'user' and item.get('content') and isinstance(item['content'][0], dict):
                user_msg = item['content'][0].get('text')
            elif item.get('role') == 'assistant' and item.get('content') and isinstance(item['content'][0], dict):
                ai_msg = item['content'][0].get('text')
        
        # 3. 튜플도 딕셔너리도 아니거나 유효한 텍스트를 찾지 못한 경우 건너뜁니다.
        if user_msg is None and ai_msg is None:
            # 유효하지 않은 항목에 대한 경고 로그를 남깁니다.
            # print(f"경고: Gradio history 항목이 유효하지 않습니다: {item}") # 이미 출력되었으므로 제거 가능
            continue

        # 4. LangChain 메시지 객체 생성 (user_msg와 ai_msg 모두 None이 아닌 경우에만)
        if user_msg:
            chat_history.append(HumanMessage(content=user_msg))
        if ai_msg:
            chat_history.append(AIMessage(content=ai_msg))

    # 현재 사용자 메시지 추가
    chat_history.append(HumanMessage(content=message))
    
    # 2. 초기 State 정의
    initial_state = AgentState(
        messages=chat_history,
        lecture_index_status="READY", 
        long_term_memory_query="" 
    )

    # 3. Agent 실행 (astream 사용)
    current_response = ""
    tool_status_message = "" # Tool 실행 중 메시지 관리를 위한 변수
    
    # LangGraph의 astream을 사용하여 비동기로 실행
    async for chunk in agent_app.astream(initial_state): 
        
        # LLM 노드 처리 (답변 스트리밍)
        if "llm_node" in chunk:
            ai_message = chunk["llm_node"]["messages"][-1]
            
            # 최종 답변 스트리밍
            if ai_message.content and not ai_message.tool_calls:
                # Tool 상태 메시지를 제거하고 새 응답을 추가
                current_response = current_response.replace(tool_status_message, "")
                current_response += ai_message.content
                yield current_response
                tool_status_message = "" # Tool 상태 초기화

        # Tool 노드 처리 (Tool 실행 알림)
        if "tool_node" in chunk:
            # Tool 실행 중임을 알리는 임시 메시지를 추가합니다.
            if not tool_status_message:
                tool_status_message = "\n\n**... Tool 실행 중. 잠시만 기다려주세요...**"
                if current_response and not current_response.endswith('\n\n'):
                     current_response += "\n\n"
                current_response += tool_status_message
                yield current_response

# PDF 업로드 및 색인 기능
def handle_pdf_upload(file):
    """
    PDF 파일을 받아 RAG 색인 파이프라인을 실행합니다.
    (A 역할의 'index_pdf_file' 함수를 호출하는 것으로 가정)
    """
    if file is None:
        return "PDF 파일을 업로드해주세요."
    
    file_path = file.name
    
    # 1. A 역할의 RAG 색인 함수 호출
    try:
        # A 역할이 구현한 RAG 색인 함수 (청크, 임베딩, Chroma DB 저장)
        index_pdf_file(file_path)
        return f"✅ '{file_path}' 파일 색인 완료. 이제 강의 내용에 대해 질문할 수 있습니다."
    except Exception as e:
        return f"❌ 파일 색인 중 오류 발생: {e}"

def create_gradio_interface():
    """
    Gradio 앱 인터페이스를 생성합니다.
    (FastAPI에 마운트할 때 호출되는 함수)
    """
    
    with gr.Blocks(title="AI 학습 코치 Agent (LangGraph + RAG)") as demo:
        gr.Markdown(
            """
            # 🎯 AI 학습 코치 / 강의자료 RAG 에이전트
            LangGraph 기반 ReAct 구조로 작동하는 지능형 학습 코치입니다.
            강의 자료(PDF)를 업로드하고 질문해 보세요!
            """
        )

        # 1. PDF 업로드 영역
        with gr.Row():
            pdf_file = gr.File(label="강의 PDF 파일 업로드", file_types=[".pdf"], type="filepath")
            index_output = gr.Textbox(label="색인 상태", value="파일을 업로드하면 RAG 색인이 시작됩니다.", interactive=False)
            
            pdf_file.upload(
                fn=handle_pdf_upload,
                inputs=[pdf_file],
                outputs=[index_output]
            )
            
        gr.Markdown("---")

        # 2. 채팅 영역
        chatbot = gr.ChatInterface(
            fn=run_agent,
            chatbot=gr.Chatbot(height=500),
            textbox=gr.Textbox(placeholder="강의 내용 또는 일반적인 질문을 입력하세요...", container=False, scale=7),
            title="AI 학습 코치 채팅",
            # 문제가 되는 버튼 인자들은 모두 제거했습니다.
        )
        
    return demo
