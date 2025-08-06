import streamlit as st
from config import Config
from openai_client import OpenAIClient
from result_processor import ResultProcessor
from ui_components import UIComponents

# 페이지 설정
st.set_page_config(
    page_title="요구사항 분석기",
    page_icon="🔍",
    layout="wide"
)

# CSS 스타일 적용
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stAlert > div {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    .stExpander {
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """세션 상태 초기화"""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'result_data' not in st.session_state:
        st.session_state.result_data = None
    if 'requirement_input' not in st.session_state:
        st.session_state.requirement_input = ""
    if 'analysis_type' not in st.session_state:
        st.session_state.analysis_type = ""
    if 'priority_level' not in st.session_state:
        st.session_state.priority_level = ""
    if 'focus_areas' not in st.session_state:
        st.session_state.focus_areas = []
    if 'checklist' not in st.session_state:
        st.session_state.checklist = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None

def main():
    # 세션 상태 초기화
    initialize_session_state()
    
    # 컴포넌트 초기화
    ui = UIComponents()
    openai_client = OpenAIClient()
    result_processor = ResultProcessor()
    
    # 헤더 렌더링
    ui.render_header()
    
    # 사용 예시와 팁 표시
    col1, col2 = st.columns(2)
    with col1:
        ui.render_examples()
    with col2:
        ui.render_tips()
    
    # 메인 입력 섹션 렌더링
    requirement_input, analysis_type, priority_level, focus_areas = ui.render_input_section()
    
    # 분석 버튼 및 유효성 검사
    should_analyze = ui.render_analysis_button(requirement_input)
    
    # 새로운 분석이 요청된 경우
    if should_analyze:
        # 이전 결과 초기화
        st.session_state.analysis_result = None
        st.session_state.result_data = None
        st.session_state.checklist = None
        st.session_state.stats = None
        
        # 현재 입력값들을 세션에 저장
        st.session_state.requirement_input = requirement_input
        st.session_state.analysis_type = analysis_type
        st.session_state.priority_level = priority_level
        st.session_state.focus_areas = focus_areas
        
        # 분석 실행
        with ui.show_loading_message("요구사항을 분석하고 있습니다..."):
            analysis_result = openai_client.analyze_requirements(
                requirement_input, 
                analysis_type, 
                focus_areas
            )
        
        if analysis_result:
            # 분석 결과를 세션에 저장
            st.session_state.analysis_result = analysis_result
            
            # 분석 결과 파싱
            result_data = result_processor.parse_analysis_result(analysis_result)
            if result_data:
                st.session_state.result_data = result_data
                
                # 요약 통계 생성 및 저장
                stats = result_processor.create_summary_stats(requirement_input, result_data)
                st.session_state.stats = stats
        else:
            ui.show_error_message("분석 결과를 생성할 수 없습니다. OpenAI API 설정을 확인해주세요.")
    
    # 저장된 분석 결과가 있으면 표시
    if st.session_state.analysis_result and st.session_state.result_data:
        st.header("📋 분석 결과")
        
        # 요약 통계 표시
        if st.session_state.stats:
            result_processor.display_summary_stats(st.session_state.stats)
        
        st.markdown("---")
        
        # 분석 결과 표시
        result_processor.display_analysis_result(st.session_state.result_data)
        
        # 분석 인사이트 표시
        if st.session_state.stats:
            insights = result_processor.get_analysis_insights(st.session_state.stats)
            if insights:
                result_processor.display_insights(insights)
        
        # 체크리스트 생성 섹션
        st.markdown("---")
        st.subheader("📝 체크리스트 생성")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("분석 결과를 바탕으로 실행 가능한 체크리스트를 생성합니다.")
        with col2:
            generate_checklist = st.button(
                "✅ 체크리스트 생성", 
                type="secondary", 
                use_container_width=True,
                key="generate_checklist_btn"
            )
        
        # 체크리스트 생성 버튼이 클릭된 경우
        if generate_checklist:
            with ui.show_loading_message("체크리스트를 생성하고 있습니다..."):
                checklist = openai_client.generate_checklist(
                    st.session_state.requirement_input, 
                    st.session_state.analysis_result, 
                    st.session_state.priority_level
                )
            
            if checklist:
                st.session_state.checklist = checklist
        
        # 저장된 체크리스트가 있으면 표시
        if st.session_state.checklist:
            st.markdown("---")
            result_processor.display_checklist(st.session_state.checklist)
            
            # 다운로드 섹션
            st.markdown("---")
            st.subheader("📥 결과 다운로드")
            
            download_content = result_processor.create_download_content(
                st.session_state.requirement_input, 
                st.session_state.analysis_result, 
                st.session_state.checklist
            )
            
            filename = result_processor.get_download_filename(st.session_state.requirement_input)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("분석 결과와 체크리스트를 마크다운 파일로 다운로드합니다.")
            with col2:
                st.download_button(
                    label="📥 분석 결과 다운로드",
                    data=download_content,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True,
                    key="download_btn"
                )
        
        # 새 분석 시작 버튼
        st.markdown("---")
        if st.button("🔄 새로운 분석 시작", type="primary", use_container_width=True):
            # 세션 상태 초기화
            for key in ['analysis_result', 'result_data', 'checklist', 'stats', 
                       'requirement_input', 'analysis_type', 'priority_level', 'focus_areas']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # 푸터 렌더링
    ui.render_footer()

if __name__ == "__main__":
    main()