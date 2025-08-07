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
    
    # Azure AI Search 설정
    AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
    AZURE_SEARCH_SERVICE_NAME = os.getenv("AZURE_SEARCH_SERVICE_NAME")
    AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
    AZURE_SEARCH_API_VERSION = os.getenv("AZURE_SEARCH_API_VERSION", "2023-11-01")
    
    # 앱 설정
    APP_TITLE = "🔍 사용자 요구사항 분석기"
    MAX_TEXT_LENGTH = 2000
    
    # 분석 설정
    DEFAULT_TEMPERATURE = 0.3
    CHECKLIST_TEMPERATURE = 0.1
    
    # PDF 검색 설정
    PDF_SEARCH_TOP_K = 5
    PDF_SEARCH_THRESHOLD = 0.7