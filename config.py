import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class Config:
    # OpenAI 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE")
    OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
    DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_LLM1")
    
    # 앱 설정
    APP_TITLE = "🔍 사용자 요구사항 분석기"
    MAX_TEXT_LENGTH = 2000
    
    # 분석 설정
    DEFAULT_TEMPERATURE = 0.3
    CHECKLIST_TEMPERATURE = 0.1