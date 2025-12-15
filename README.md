# 📘 CPU-Agent: LangGraph 기반 AI 학습 코치

## 1. 프로젝트 개요

**CPU-Agent**는 강의 자료(PDF)를 기반으로 학생의 질문에 답변하고,
필요에 따라 다양한 도구를 사용하며, 학습 취약점을 장기적으로 기억하는
**LangGraph 기반 AI 학습 코치 Agent**입니다.

본 프로젝트는 *생성형 AI 응용* 수업의 Final Project로,
수업에서 다룬 **Tool Calling, RAG, Memory, ReAct, LangGraph, Gradio UI**를
하나의 통합 Agent 시스템으로 구현하는 것을 목표로 합니다.

---

## 2. 핵심 컨셉 (한 줄 요약)

> **“강의 PDF를 넣어두면,
> AI가 관련 내용을 찾아보고(RAG),
> 계산·시간·검색 도구를 활용하며,
> 학생의 학습 취약점을 기억하는 학습 코치 Agent”**

---

## 3. 주요 기능

### ✅ 1) LLM (gpt-4o-mini)

* OpenAI API 기반
* Tool Calling 및 Reasoning 수행

---

### ✅ 2) Tool Calling

Agent는 상황에 따라 다음 도구들을 호출합니다.

* `calculator` : 수식 계산
* `time_now` : 현재 시간 확인
* `google_search` : 외부 정보 검색 (mock 기반 Tool)
* `rag_search` : 강의 자료 검색
* `read_memory` / `write_memory` : 학습 메모리 관리

---

### ✅ 3) RAG (Retrieval-Augmented Generation)

* 강의 PDF 업로드
* 텍스트 분할 → 임베딩 → ChromaDB 저장
* 질문 시 관련 강의 내용을 검색하여 답변 생성

---

### ✅ 4) Memory 시스템

* **Short-Term Memory**

  * LangGraph State(`messages`)를 사용하여
    세션 내 대화 흐름과 Tool 결과 유지

* **Long-Term Memory**

  * ChromaDB Persistent Storage를 사용하여
    학생의 학습 취약 단원 및 중요 정보 저장

* **Reflection**

  * 대화 종료 시 LLM이 자동으로
    메모리 저장 여부를 판단하여 Long-Term Memory에 기록

---

### ✅ 5) LangGraph 기반 ReAct Agent

* `Think → Act → Observe` 흐름을 그래프로 구성
* 노드 구성:

  * `llm_node`
  * `tool_node`
  * `reflection_node`
* 조건부 Edge를 통해 Tool 호출 여부 결정

---

### ✅ 6) UI (Gradio + FastAPI)

* Gradio 기반 채팅 UI
* PDF 업로드 및 색인 기능 제공
* FastAPI에 mount하여 서버 실행

---

## 4. 시스템 구조

```
AI Study Coach Agent
│
├── UI Layer
│   └── Gradio + FastAPI
│
├── Agent Orchestration
│   └── LangGraph StateGraph
│       ├── llm_node
│       ├── tool_node
│       └── reflection_node
│
├── Core Logic
│   ├── LLM Client
│   ├── Tool Calling
│   ├── RAG Pipeline
│   └── Memory System
│
└── Data Store
    ├── Lecture PDF Index (ChromaDB)
    └── Memory Store (ChromaDB)
```

---

## 5. 프로젝트 폴더 구조

```
cpu-agent/
├── app/
│   ├── main.py
│   ├── llm_client.py
│   ├── tools/
│   ├── rag/
│   ├── memory/
│   ├── graph/
│   └── ui/
├── requirements.txt
├── .env.template
└── README.md
```

---

## 6. 실행 방법

### 1️⃣ 환경 설정

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ 환경 변수 설정

`.env` 파일 생성 후 OpenAI API Key 입력

```env
OPENAI_API_KEY=your_api_key
```

### 3️⃣ 서버 실행

```bash
uvicorn app.main:app --reload
```

### 4️⃣ 접속

브라우저에서 아래 주소로 접속합니다.

```
http://127.0.0.1:8000/gradio
```

---

## 7. 팀 구성 및 역할

| 역할 | 담당 내용                                 |
| -- | ------------------------------------- |
| A (오동석) | LLM Client, Tool 로직, RAG, Memory 시스템  |
| B (김희준) | LangGraph 구조, Agent Flow, UI, FastAPI |

---

## 8. 기대 효과

* 강의 자료 기반 **맞춤형 학습 보조**
* 반복 질문을 통한 **취약 단원 자동 분석**
* 수업에서 배운 Agent 기술을 **하나의 시스템으로 통합**

---

## 9. 사용 기술

* OpenAI GPT-4o-mini
* LangGraph
* ChromaDB
* Sentence-Transformers
* Gradio
* FastAPI

---

## 10. 마무리

본 프로젝트는 단순 기능 구현을 넘어,
**Agent 설계 관점에서 LLM, Tool, Memory, Graph를 통합한 학습 보조 시스템**을
구현하는 데 초점을 두었습니다.