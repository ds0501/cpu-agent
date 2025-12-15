import uvicorn
from fastapi import FastAPI
from gradio.routes import mount_gradio_app
from app.ui.gradio_app import create_gradio_interface

# 1. FastAPI 애플리케이션 생성
app = FastAPI(
    title="AI Study Coach Agent Backend",
    description="FastAPI server hosting the Gradio UI for the LangGraph Agent.",
    version="1.0.0",
)

# 2. Gradio 인터페이스 생성
gradio_app = create_gradio_interface()

# 3. Gradio 애플리케이션을 FastAPI에 마운트
# /gradio/ 경로로 접속하면 Gradio UI가 보입니다.
app = mount_gradio_app(
    app, 
    gradio_app, 
    path="/gradio"
)

# 루트 경로 ("/")로 접속하면 자동으로 Gradio UI로 리다이렉트되도록 설정 (선택 사항)
@app.get("/")
async def root():
    return {"message": "Access the AI Study Coach UI at /gradio"}

# 서버 실행 (개발 환경용)
if __name__ == "__main__":
    # `uvicorn.run()`을 사용하여 서버를 실행합니다.
    # Gradio mount 시점과 uvicorn 실행 시점의 경로 처리가 중요합니다.
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    print("FastAPI 서버 시작: http://127.0.0.1:8000/gradio")
    print("LangGraph Agent가 준비되었습니다. 'uvicorn app.main:app --reload' 명령으로 실행하세요.")