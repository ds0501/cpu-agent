"""
환경 설정
"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API 설정 (필수!)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"

# Google Search API 설정 (현재 미사용 - Mock 버전 사용 중)
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Chroma DB 설정
CHROMA_PERSIST_DIR = "./chroma_db"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"