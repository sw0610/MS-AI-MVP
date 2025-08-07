import json
import streamlit as st
from datetime import datetime

class ResultProcessor:
    def __init__(self):
        pass
    
    def parse_analysis_result(self, analysis_result):
        # JSON 분석 결과를 파싱하고 표시하는 함수
        if not analysis_result:
            st.error("분석 결과가 없습니다.")
            return None
        
        try:
            # JSON 파싱 시도
            result_data = json.loads(analysis_result)
            return result_data
        except json.JSONDecodeError:
            st.warning("JSON 파싱에 실패했습니다. 원본 텍스트를 표시합니다.")
            return {"raw_text": analysis_result}
    
    def display_analysis_result(self, result_data):
        # 분석 결과를 화면에 표시하는 함수
        if not result_data:
            return
        
        # 원본 텍스트인 경우
        if "raw_text" in result_data:
            st.write(result_data["raw_text"])
            return
        
        manual_refs = result_data.get("manual_references", [])
        if manual_refs:
            st.subheader("📚 시스템 매뉴얼 참고사항")
            for i, ref in enumerate(manual_refs, 1):
                st.info(f"{i}. {ref}")
        
        # 구조화된 데이터인 경우
        # 요약
        if "analysis_summary" in result_data:
            st.subheader("📝 요구사항 요약")
            st.info(result_data.get("analysis_summary", "요약 정보 없음"))
        
        # 비즈니스 영향도
        if "business_impact" in result_data:
            st.subheader("💼 비즈니스 영향도")
            st.write(result_data.get("business_impact", "영향도 분석 없음"))
        
        # 확인 필요사항
        clarifications = result_data.get("clarification_needed", [])
        if clarifications:
            st.subheader("❓ 확인이 필요한 사항들")
            
            # 우선순위별로 정렬
            high_priority = [item for item in clarifications if item.get('priority') == '높음']
            medium_priority = [item for item in clarifications if item.get('priority') == '보통']
            low_priority = [item for item in clarifications if item.get('priority') == '낮음']
            
            for priority_group, priority_name, color in [
                (high_priority, "🔴 높음", "red"),
                (medium_priority, "🟡 보통", "orange"), 
                (low_priority, "🟢 낮음", "green")
            ]:
                if priority_group:
                    st.markdown(f"**우선순위: {priority_name}**")
                    for i, item in enumerate(priority_group, 1):
                        category = item.get('category', '기타')
                        question = item.get('question', '질문 없음')
                        reason = item.get('reason', '이유 없음')
                        manual_ref = item.get('manual_reference', '')
                        
                        with st.expander(f"[{category}] {question}"):
                            st.write("**확인이 필요한 이유:**")
                            st.write(reason)
                            if manual_ref:
                                st.write("**매뉴얼 참고사항:**")
                                st.write(manual_ref)
                    st.markdown("---")
                
        # 잠재적 이슈
        issues = result_data.get("potential_issues", [])
        if issues:
            st.subheader("⚠️ 잠재적 문제점들")
            for i, issue in enumerate(issues, 1):
                st.warning(f"{i}. {issue}")
    
    def display_checklist(self, checklist):
        # 체크리스트를 화면에 표시하는 함수
        if not checklist:
            st.error("체크리스트를 생성할 수 없습니다.")
            return
        
        st.header("✅ 개발 체크리스트")
        st.markdown(checklist)
    
    def create_summary_stats(self, requirement_text, result_data):
        # 분석 결과 요약 통계를 생성하는 함수
        stats = {
            'requirement_length': len(requirement_text),
            'requirement_words': len(requirement_text.split()),
            'clarifications_count': 0,
            'issues_count': 0,
            'high_priority_count': 0
        }
        
        if result_data and isinstance(result_data, dict):
            clarifications = result_data.get("clarification_needed", [])
            issues = result_data.get("potential_issues", [])
            high_priority = [item for item in clarifications if item.get('priority') == '높음']
            
            stats['clarifications_count'] = len(clarifications)
            stats['issues_count'] = len(issues)
            stats['high_priority_count'] = len(high_priority)
        
        return stats
    
    def display_summary_stats(self, stats):
        # 요약 통계를 표시하는 함수
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("요구사항 길이", f"{stats['requirement_length']}자")
        
        with col2:
            st.metric("단어 수", f"{stats['requirement_words']}개")
        
        with col3:
            st.metric("확인사항", f"{stats['clarifications_count']}개")
        
        with col4:
            st.metric("긴급 확인사항", f"{stats['high_priority_count']}개", 
                     delta=None if stats['high_priority_count'] == 0 else "중요!")
    
    def get_analysis_insights(self, stats):
        # 분석 결과에 대한 인사이트를 생성하는 함수
        insights = []
        
        if stats['high_priority_count'] > 3:
            insights.append("🔴 긴급 확인사항이 많습니다. 요구사항을 더 구체화할 필요가 있어 보입니다.")
        
        if stats['clarifications_count'] > 8:
            insights.append("⚠️ 확인사항이 매우 많습니다. 요구사항을 단계별로 나누어 진행하는 것을 고려해보세요.")
        
        if stats['clarifications_count'] < 3:
            insights.append("✅ 비교적 명확한 요구사항입니다. 추가 확인사항이 적습니다.")
        
        if stats['requirement_words'] < 10:
            insights.append("📝 요구사항이 너무 간단할 수 있습니다. 더 구체적인 설명이 있으면 더 정확한 분석이 가능합니다.")
        
        return insights
    
    def display_insights(self, insights):
        # 인사이트를 표시하는 함수
        if insights:
            st.subheader("💡 분석 인사이트")
            for insight in insights:
                st.info(insight)