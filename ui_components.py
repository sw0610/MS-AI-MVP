import streamlit as st
from config import Config

class UIComponents:
    def __init__(self):
        self.config = Config()
    
    def render_header(self):
        # 앱 헤더를 렌더링하는 함수
        st.title(Config.APP_TITLE)
        st.markdown("---")
        st.write("사용자 요구사항을 입력하면 구현 전 확인이 필요한 사항들을 분석하고 체크리스트를 생성합니다.")
    
    def render_input_section(self):
        # 입력 섹션을 렌더링하는 함수
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.header("📝 요구사항 입력")
            requirement_input = st.text_area(
                "사용자 요구사항을 입력하세요:",
                height=200,
                placeholder="예시: 챗봇 링크를 메인 화면에 추가해주세요.\n예시: 계약금액이 구매요청 금액을 넘어가지 않게 해주세요.\n예시: 엑셀 업로드 시 중복 데이터는 자동으로 제거해주세요.",
                help="구현하고자 하는 기능이나 변경사항을 구체적으로 입력해주세요.",
                max_chars=Config.MAX_TEXT_LENGTH
            )
            
            # 글자 수 표시
            if requirement_input:
                char_count = len(requirement_input)
                st.caption(f"입력된 글자 수: {char_count}/{Config.MAX_TEXT_LENGTH}")
        
        with col2:
            st.header("⚡ 분석 옵션")
            analysis_type = st.selectbox(
                "분석 유형:",
                ["기본 분석", "상세 분석"],
                help="상세 분석은 더 많은 확인사항을 도출합니다."
            )
            
            priority_level = st.selectbox(
                "우선순위 수준:",
                ["높음", "보통", "낮음"],
                index=1,
                help="체크리스트의 상세도를 결정합니다."
            )
            
            # 집중 분석 영역
            st.subheader("🎯 집중 분석 영역")
            focus_areas = []
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                if st.checkbox("UI/UX", value=True):
                    focus_areas.append("UI/UX")
                if st.checkbox("비즈니스 로직", value=True):
                    focus_areas.append("비즈니스 로직")
                if st.checkbox("데이터 처리"):
                    focus_areas.append("데이터 처리")
            
            with col2_2:
                if st.checkbox("권한 관리"):
                    focus_areas.append("권한 관리")
                if st.checkbox("성능"):
                    focus_areas.append("성능")
                if st.checkbox("보안"):
                    focus_areas.append("보안")
        
        return requirement_input, analysis_type, priority_level, focus_areas
    
    def render_analysis_button(self, requirement_input):
        # 분석 버튼을 렌더링하고 유효성 검사를 수행하는 함수
        if st.button("🔍 요구사항 분석하기", type="primary", use_container_width=True):
            # 입력 유효성 검사
            if not requirement_input.strip():
                st.error("요구사항을 입력해주세요.")
                return False
            
            if len(requirement_input.strip()) < 5:
                st.error("요구사항을 더 구체적으로 입력해주세요. (최소 5자)")
                return False
            
            return True
        
        return False
    
    def render_examples(self):
        # 사용 예시를 렌더링하는 함수
        with st.expander("💡 사용 예시 보기"):
            tab1, tab2, tab3, tab4 = st.tabs(["UI 기능", "비즈니스 규칙", "데이터 처리", "시스템 연동"])
            
            with tab1:
                st.markdown("""
                **UI 기능 추가 예시:**
                ```
                챗봇 링크를 메인 화면에 추가해주세요
                ```
                
                **분석 결과 예시:**
                - 메인 화면의 어느 위치에 추가할지?
                - 링크 클릭시 동작 방식은? (팝업/새창/리다이렉션)
                - 아이콘 디자인은 언제 제공 가능한지?
                - 모든 사용자에게 노출할지, 권한별 제어가 필요한지?
                """)
            
            with tab2:
                st.markdown("""
                **비즈니스 규칙 변경 예시:**
                ```
                계약금액이 구매요청 금액을 넘어가지 않게 해주세요
                ```
                
                **분석 결과 예시:**
                - 모든 계약 유형에 적용하는지? (물자/공사/용역)
                - 기존 진행중인 계약도 포함하는지?
                - 한도 초과시 처리 방식은? (경고/차단)
                - 예외 상황이나 특별 승인 프로세스가 있는지?
                """)
            
            with tab3:
                st.markdown("""
                **데이터 처리 예시:**
                ```
                엑셀 업로드 시 중복 데이터는 자동으로 제거해주세요
                ```
                
                **분석 결과 예시:**
                - 중복 판단 기준은? (전체 행/특정 컬럼)
                - 중복 발견시 처리 방법은? (첫번째 유지/마지막 유지/사용자 선택)
                - 사용자에게 알림을 제공할지?
                - 제거된 데이터의 로그를 남길지?
                """)
            
            with tab4:
                st.markdown("""
                **시스템 연동 예시:**
                ```
                결재 완료 시 자동으로 회계시스템에 전송해주세요
                ```
                
                **분석 결과 예시:**
                - 어떤 결재 유형에 적용하는지?
                - 전송 실패시 재시도 로직은?
                - 회계시스템 점검 중일 때 처리는?
                - 전송 완료 확인 방법은?
                """)
    
    def render_tips(self):
        # 사용 팁을 렌더링하는 함수
        with st.expander("📚 효과적인 요구사항 작성 팁"):
            st.markdown("""
            **명확한 요구사항 작성을 위한 가이드:**
            
            ✅ **좋은 예시:**
            - "로그인 화면에서 비밀번호 찾기 버튼을 추가해주세요"
            - "월별 매출 보고서에 전년 대비 증감률 컬럼을 추가해주세요"
            - "계약서 승인 시 자동으로 담당자에게 이메일 알림을 보내주세요"
            
            ❌ **모호한 예시:**
            - "시스템을 개선해주세요"
            - "더 편리하게 만들어주세요"
            - "보고서를 수정해주세요"
            
            **포함하면 좋은 정보:**
            - 구체적인 화면이나 기능명
            - 예상되는 사용자 그룹
            - 원하는 동작 방식
            - 기대하는 결과
            """)
    
    def render_footer(self):
        # 푸터를 렌더링하는 함수
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666; padding: 20px;'>
                <small>
                    💡 이 도구는 요구사항 분석을 도와주는 도구입니다.<br>
                </small>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    def show_loading_message(self, message="처리 중입니다..."):
        # 로딩 메시지를 표시하는 함수
        return st.spinner(message)
    
    def show_success_message(self, message):
        # 성공 메시지를 표시하는 함수
        st.success(message)
    
    def show_error_message(self, message):
        # 에러 메시지를 표시하는 함수
        st.error(message)
    
    def show_warning_message(self, message):
        # 경고 메시지를 표시하는 함수
        st.warning(message)