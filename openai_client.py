from openai import AzureOpenAI, OpenAI
import streamlit as st
from config import Config
from pdf_search_client import PDFSearchClient
import json

class OpenAIClient:
    def __init__(self):
        # OpenAI 클라이언트 초기화
        if Config.OPENAI_API_TYPE == "azure":
            self.client = AzureOpenAI(
                api_key=Config.OPENAI_API_KEY,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                api_version=Config.OPENAI_API_VERSION
            )
            self.deployment_name = Config.DEPLOYMENT_NAME
        else:
            self.client = OpenAI(
                api_key=Config.OPENAI_API_KEY
            )
            self.deployment_name = Config.DEPLOYMENT_NAME  # 또는 원하는 모델명
        
        # PDF 검색 클라이언트 초기화
        self.pdf_client = PDFSearchClient()
    
    def get_response(self, messages, temperature=None):
        # OpenAI API를 통해 응답을 받는 함수
        if temperature is None:
            temperature = Config.DEFAULT_TEMPERATURE
            
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI API 오류: {e}")
            return None
    
    def analyze_requirements(self, requirement_text, analysis_type="기본 분석", focus_areas=None):
        # 사용자 요구사항을 분석하고 확인이 필요한 사항들을 찾는 함수
        
        # 1. 기본 분석 실행
        basic_analysis = self._basic_analysis(requirement_text, analysis_type, focus_areas)
        
        # 2. PDF 매뉴얼 기반 추가 분석 (가능한 경우)
        manual_analysis = None
        if self.pdf_client.retriever and self.pdf_client.llm:
            manual_analysis = self.pdf_client.analyze_with_manual(requirement_text, focus_areas)
        
        # 3. 분석 결과 통합
        if manual_analysis:
            return self._combine_analysis_results(basic_analysis, manual_analysis)
        else:
            return basic_analysis
    
    def _basic_analysis(self, requirement_text, analysis_type, focus_areas):
        """기본 요구사항 분석"""
        focus_text = ""
        if focus_areas:
            focus_text = f"\n특히 다음 영역에 집중해서 분석해주세요: {', '.join(focus_areas)}\n"
        
        base_prompt = f"""
당신은 시스템 분석 전문가입니다. 다음 사용자 요구사항을 분석하여 구현 전 반드시 요청자에게 확인이 필요한 사항들을 찾아주세요.

사용자 요구사항:
{requirement_text}

{focus_text}

분석해야 할 관점들:
1. 기능의 정확한 위치나 범위 (어디에, 어떤 화면에서, 어떤 조건에서)
2. 사용자 인터랙션 방식 (클릭, 팝업, 리다이렉션, 새창 등)
3. 데이터 처리 방식과 예외상황 처리
4. 권한과 접근 제어 (누가 사용할 수 있는지)
5. UI/UX 세부사항 (디자인, 아이콘, 텍스트, 위치 등)
6. 비즈니스 규칙의 적용 범위와 예외상황
7. 기존 기능과의 연동 및 영향도
8. 성능 및 보안 고려사항

실무에서 자주 발생하는 상황들을 고려해주세요:
- "메인 화면에 추가"라고 하면 구체적인 위치와 우선순위 확인 필요
- "계약서에 적용"이라고 하면 계약 유형별 예외사항 확인 필요
- "자동으로 처리"라고 하면 실패 시 대안 처리 방안 확인 필요

다음 JSON 형식으로 응답해주세요:
{{
    "analysis_summary": "요구사항 요약",
    "clarification_needed": [
        {{
            "category": "카테고리명",
            "question": "구체적인 확인 질문",
            "reason": "왜 이 확인이 필요한지 설명",
            "priority": "높음/보통/낮음"
        }}
    ],
    "potential_issues": [
        "예상되는 잠재적 문제점들"
    ],
    "business_impact": "비즈니스 영향도 분석"
}}
"""

        messages = [
            {"role": "system", "content": "당신은 요구사항 분석 전문가입니다. 실무진이 놓치기 쉬운 세부사항들을 찾아 구체적인 확인 질문을 제시합니다. 특히 한국의 업무 환경과 시스템 특성을 고려합니다."},
            {"role": "user", "content": base_prompt}
        ]
        
        return self.get_response(messages)
    
    def _combine_analysis_results(self, basic_analysis, manual_analysis):
        """기본 분석과 매뉴얼 기반 분석 결과를 통합"""
        try:
            basic_data = json.loads(basic_analysis) if isinstance(basic_analysis, str) else basic_analysis
            manual_data = json.loads(manual_analysis["analysis_result"]) if isinstance(manual_analysis["analysis_result"], str) else manual_analysis["analysis_result"]
            
            # 통합된 분석 결과 생성
            combined_result = {
                "analysis_summary": f"{basic_data.get('analysis_summary', '')}\n\n[매뉴얼 기반 추가 분석]\n{manual_data.get('analysis_summary', '')}",
                "manual_references": manual_data.get('manual_references', []),
                "clarification_needed": basic_data.get('clarification_needed', []) + manual_data.get('clarification_needed', []),
                "potential_issues": basic_data.get('potential_issues', []) + manual_data.get('potential_issues', []),
                "business_impact": f"{basic_data.get('business_impact', '')}\n\n[시스템 연관성]\n{manual_data.get('business_impact', '')}",
                "manual_search_info": {
                    "search_keywords": manual_analysis["search_info"]["search_keywords"],
                    "doc_count": len(manual_analysis["search_info"]["relevant_docs"])
                }
            }
            
            return json.dumps(combined_result, ensure_ascii=False, indent=2)
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            st.warning(f"분석 결과 통합 중 오류 발생: {e}")
            return basic_analysis
    
    def generate_checklist(self, requirement_text, analysis_result, priority_level="보통"):
        # 분석 결과를 바탕으로 체크리스트를 생성하는 함수
        priority_instruction = {
            "높음": "매우 상세하고 철저한 체크리스트를 만들어주세요.",
            "보통": "실무에 필요한 핵심 항목들로 체크리스트를 만들어주세요.",
            "낮음": "꼭 필요한 최소한의 항목들로 간단한 체크리스트를 만들어주세요."
        }.get(priority_level, "실무에 필요한 핵심 항목들로 체크리스트를 만들어주세요.")
        
        prompt = f"""
다음 요구사항 분석 결과를 바탕으로 개발자와 기획자가 사용할 수 있는 체크리스트를 생성해주세요.

우선순위: {priority_level}
{priority_instruction}

요구사항: {requirement_text}
분석 결과: {analysis_result}

체크리스트는 다음 형식으로 작성해주세요:
- [ ] 구체적인 확인/작업 항목 (담당자: 기획/개발/디자인)
- 각 항목은 실제로 체크할 수 있는 구체적인 내용이어야 합니다.
- 담당자를 명시하여 역할을 명확히 해주세요.
- 매뉴얼 참고사항이 있다면 포함해주세요.

## 📋 개발 전 확인사항
- [ ] 예시 항목 (담당자: 기획)

## 🔧 개발 중 확인사항  
- [ ] 예시 항목 (담당자: 개발)

## ✅ 개발 후 검증사항
- [ ] 예시 항목 (담당자: 기획/개발)

## 🚀 배포 전 최종 점검
- [ ] 예시 항목 (담당자: 전체)
"""

        messages = [
            {"role": "system", "content": "당신은 프로젝트 관리 전문가입니다. 실무에서 바로 사용할 수 있는 구체적이고 실행 가능한 체크리스트를 생성합니다. 시스템 매뉴얼 정보가 있다면 이를 반영합니다."},
            {"role": "user", "content": prompt}
        ]
        
        return self.get_response(messages, temperature=Config.CHECKLIST_TEMPERATURE)
    
    def get_manual_context(self, requirement_text):
        """매뉴얼 컨텍스트 정보 반환"""
        if self.pdf_client.retriever:
            return self.pdf_client.get_system_context(requirement_text)
        return None