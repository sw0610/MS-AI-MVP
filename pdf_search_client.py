from langchain_community.retrievers import AzureAISearchRetriever
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import streamlit as st
from config import Config

class PDFSearchClient:
    def __init__(self):
        self.config = Config()
        
        # Azure AI Search Retriever 초기화
        try:
            self.retriever = AzureAISearchRetriever(
                service_name=self.config.AZURE_SEARCH_SERVICE_NAME,
                index_name=self.config.AZURE_SEARCH_INDEX_NAME,
                top_k=self.config.PDF_SEARCH_TOP_K,
                content_key="chunk",
                api_key=self.config.AZURE_SEARCH_ADMIN_KEY
            )
        except Exception as e:
            st.warning(f"PDF 검색 기능을 사용할 수 없습니다: {e}")
            self.retriever = None
        
        # LangChain용 LLM 초기화
        try:
            self.llm = AzureChatOpenAI(
                deployment_name=self.config.DEPLOYMENT_NAME,
                temperature=self.config.DEFAULT_TEMPERATURE
            )
        except Exception as e:
            st.error(f"LangChain LLM 초기화 실패: {e}")
            self.llm = None
    
    def format_docs(self, docs):
        """검색된 문서들을 포맷팅"""
        return "\n\n".join([doc.page_content for doc in docs])
    
    def search_manual_content(self, requirement_text):
        """매뉴얼에서 요구사항과 관련된 내용 검색"""
        if not self.retriever or not self.llm:
            return None
        
        try:
            # 검색 쿼리 생성 프롬프트
            search_prompt = ChatPromptTemplate.from_template(
                """다음 사용자 요구사항과 관련된 시스템 매뉴얼 내용을 검색하기 위한 키워드를 생성해주세요.
                
                요구사항: {requirement}
                
                검색할 키워드 (한국어): """
            )
            
            # 검색 키워드 생성
            search_chain = search_prompt | self.llm | StrOutputParser()
            search_keywords = search_chain.invoke({"requirement": requirement_text})
            
            # 매뉴얼에서 관련 내용 검색
            docs = self.retriever.invoke(search_keywords)
            
            if not docs:
                return None
            
            return {
                "search_keywords": search_keywords,
                "relevant_docs": docs,
                "formatted_content": self.format_docs(docs)
            }
            
        except Exception as e:
            st.error(f"매뉴얼 검색 중 오류 발생: {e}")
            return None
    
    def analyze_with_manual(self, requirement_text, focus_areas=None):
        """매뉴얼 내용을 참고하여 요구사항 분석"""
        if not self.retriever or not self.llm:
            return None
        
        # 매뉴얼에서 관련 내용 검색
        search_result = self.search_manual_content(requirement_text)
        
        if not search_result:
            return None
        
        focus_text = ""
        if focus_areas:
            focus_text = f"\n특히 다음 영역에 집중해서 분석해주세요: {', '.join(focus_areas)}\n"
        
        # 매뉴얼 내용을 포함한 분석 프롬프트
        analysis_prompt = ChatPromptTemplate.from_template(
            """당신은 시스템 분석 전문가입니다. 
            사용자 요구사항과 시스템 매뉴얼 내용을 참고하여 구현 전 요청자에게 반드시 확인이 필요한 사항들을 분석해주세요.

            사용자 요구사항:
            {requirement}

            관련 시스템 매뉴얼 내용:
            {manual_content}
            {focus_text}

            매뉴얼 내용을 바탕으로 다음을 분석해주세요:
            1. 현재 시스템의 관련 기능이나 제약사항
            2. 기존 기능과의 연동 포인트
            3. 시스템 아키텍처 상 고려사항
            4. 데이터 구조나 비즈니스 로직 관련 확인사항
            5. 권한이나 보안 정책 관련 사항

            다음 JSON 형식으로 응답해주세요:
            {{
                "analysis_summary": "요구사항과 시스템 매뉴얼 기반 종합 분석",
                "manual_references": [
                    "매뉴얼에서 참고한 주요 내용들"
                ],
                "clarification_needed": [
                    {{
                        "category": "카테고리명",
                        "question": "구체적인 확인 질문",
                        "reason": "왜 이 확인이 필요한지 설명 (매뉴얼 내용 포함)",
                        "priority": "높음/보통/낮음",
                        "manual_reference": "관련 매뉴얼 섹션이나 내용"
                    }}
                ],
                "potential_issues": [
                    "매뉴얼 기반으로 예상되는 잠재적 문제점들"
                ],
                "business_impact": "비즈니스 영향도 분석 (기존 시스템과의 연관성 포함)"
            }}
            """
        )
        
        try:
            # 분석 실행
            analysis_chain = analysis_prompt | self.llm | StrOutputParser()
            analysis_result = analysis_chain.invoke({
                "requirement": requirement_text,
                "manual_content": search_result["formatted_content"],
                "focus_text": focus_text
            })
            
            return {
                "analysis_result": analysis_result,
                "search_info": search_result
            }
            
        except Exception as e:
            st.error(f"매뉴얼 기반 분석 중 오류 발생: {e}")
            return None
    
    def get_system_context(self, requirement_text):
        """요구사항과 관련된 시스템 컨텍스트 정보 반환"""
        search_result = self.search_manual_content(requirement_text)
        
        if not search_result:
            return None
        
        return {
            "search_keywords": search_result["search_keywords"],
            "doc_count": len(search_result["relevant_docs"]),
            "content_preview": search_result["formatted_content"][:500] + "..." if len(search_result["formatted_content"]) > 500 else search_result["formatted_content"]
        }