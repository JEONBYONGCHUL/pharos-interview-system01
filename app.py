import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import json
import os
import uuid
import streamlit.components.v1 as components

# --- [1] 페이지 기본 설정 ---
st.set_page_config(
    page_title="파로스 서류 기반 모의면접 트레이너 1.5",
    page_icon="logo.png" if os.path.exists("logo.png") else "🎓",
    layout="wide"
)

# --- [디자인 스타일 CSS] ---
st.markdown("""
<style>
    * {
        word-break: keep-all; 
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* 메인 및 서브 버튼 곤색 통일 */
    div.stButton > button[kind="primary"], div.stButton > button[kind="secondary"] {
        background-color: #1e293b !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        padding: 0.5rem 1rem !important;
    }
    div.stButton > button:hover {
        background-color: #0f172a !important;
    }
    
    /* 상단 배너 */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .brand-section {
        text-align: center;
        margin-bottom: 10px;
    }
    
    button[title="View fullscreen"], [data-testid="StyledFullScreenButton"] {
        display: none !important;
    }
    [data-testid="stImage"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    /* 라디오 버튼 박스 너비 100% 꽉 채우기 및 정렬 */
    div[data-testid="stRadio"] {
        width: 100% !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        background-color: #f8fafc !important;
        padding: 15px 20px !important;
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
        box-sizing: border-box !important;
    }
    div[role="radiogroup"] > label {
        flex: 1 !important;
        justify-content: center !important;
        margin: 0 !important;
    }
    
    div[role="radiogroup"] label[data-baseweb="radio"] div:first-child {
        border-color: #1e293b !important;
    }
    div[role="radiogroup"] label[data-baseweb="radio"] div:first-child > div {
        background-color: #1e293b !important;
    }
    
    @media (max-width: 600px) {
        div[data-testid="stRadio"] > div[role="radiogroup"] {
            flex-direction: column !important;
            padding: 15px !important;
        }
        div[role="radiogroup"] > label {
            justify-content: flex-start !important;
            margin-bottom: 10px !important;
            width: 100% !important;
        }
    }
    
    .custom-divider {
        margin: 15px 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --- [2] 구글 시트 DB 연결 함수 ---
def init_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    if "GCP_JSON" in st.secrets:
        creds_dict = json.loads(st.secrets["GCP_JSON"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        json_files = [f for f in os.listdir('.') if f.endswith('.json') and ('gen-lang' in f or 'ais-gemini' in f)]
        if json_files:
            creds = ServiceAccountCredentials.from_json_keyfile_name(json_files[0], scope)
        else:
            return None
    client = gspread.authorize(creds)
    sheet = client.open("파로스모의면접1.5회원DB").sheet1
    return sheet

# --- [3] 메인 화면 및 로그인/첫 접속 라우팅 ---
def auth_screen():
    components.html(
        """
        <script>
        const inputs = window.parent.document.querySelectorAll('input');
        for (let i = 0; i < inputs.length; i++) {
            inputs[i].setAttribute('autocomplete', 'new-password');
            inputs[i].setAttribute('data-lpignore', 'true');
        }
        </script>
        """,
        height=0, width=0
    )

    st.markdown("""
        <div class="main-header">
            <h2 style='margin: 0; font-size: 1.6rem;'>파로스 서류 기반 모의면접 트레이너</h2>
            <p style='margin: 5px 0 0 0; color: #94a3b8; font-size: 0.9rem;'>맞춤형 면접 질문 추출 및 실전 구술 음성 지원 시스템</p>
        </div>
    """, unsafe_allow_html=True)

    # 비율 조정을 통한 로고 완벽 중앙 배치
    col_logo1, col_logo2, col_logo3 = st.columns([4, 1, 4])
    with col_logo2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
    
    st.markdown("""
        <div class="brand-section">
            <b style="color: #1e293b; font-size: 1.1rem;">네이버프리미엄콘텐츠 파로스대입랩</b><br>
            <a href="https://contents.premium.naver.com/pharoslab/jinhak" target="_blank" style="color: #2563eb; text-decoration: none; font-size: 0.9rem;">https://contents.premium.naver.com/pharoslab/jinhak</a>
        </div>
        <hr class="custom-divider">
    """, unsafe_allow_html=True)

    if 'view_mode' not in st.session_state:
        st.session_state['view_mode'] = 'login'

    # ---------------- [A] 로그인 화면 ----------------
    if st.session_state['view_mode'] == 'login':
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div style='text-align: center; color: #1e293b; font-size: 1.8rem; font-weight: 700; margin-bottom: 10px;'>로그인</div>", unsafe_allow_html=True)
            
            login_id = st.text_input("아이디", key="login_id")
            login_pw = st.text_input("비밀번호", type="password", key="login_pw")
            
            # 구글 비밀번호 팝업 가림을 원천 차단하기 위한 물리적 빈 공간
            st.markdown("<div style='height: 110px;'></div>", unsafe_allow_html=True)

            if st.button("로그인", type="primary", use_container_width=True):
                if not login_id or not login_pw:
                    st.error("아이디와 비밀번호를 모두 입력해주세요.")
                else:
                    try:
                        sheet = init_connection()
                        if not sheet:
                            st.error("데이터베이스 연결에 실패했습니다.")
                            return
                        
                        records = sheet.get_all_records()
                        user_row = None
                        row_idx = 0

                        for idx, record in enumerate(records):
                            if str(record.get('아이디')) == login_id:
                                user_row = record
                                row_idx = idx + 2
                                break

                        if not user_row:
                            st.error("존재하지 않는 아이디입니다.")
                        elif str(user_row.get('비밀번호')) != login_pw:
                            st.error("비밀번호가 일치하지 않습니다.")
                        else:
                            expire_date = datetime.strptime(str(user_row.get('만료일')), "%Y-%m-%d")
                            if datetime.now() > expire_date:
                                st.error("⚠️ 이용 기간이 만료되었습니다.")
                                return

                            devices = [str(user_row.get('기기1')), str(user_row.get('기기2')), str(user_row.get('기기3'))]
                            if 'device_token' not in st.session_state:
                                st.session_state['device_token'] = str(uuid.uuid4())
                            
                            current_device = st.session_state['device_token']
                            matched_slot = None
                            empty_slot = None

                            for i, d in enumerate(devices):
                                if d == current_device:
                                    matched_slot = i + 1
                                elif d == "" or d == "0":
                                    if empty_slot is None:
                                        empty_slot = i + 1

                            if matched_slot is None:
                                if empty_slot is not None:
                                    sheet.update_cell(row_idx, 5 + empty_slot, current_device)
                                    st.success("로그인 성공! 새로운 기기가 등록되었습니다.")
                                else:
                                    st.error("🚫 동시 접속 기기 초과! (최대 3대)")
                                    return
                            else:
                                st.success("로그인 성공!")

                            st.session_state['logged_in'] = True
                            st.session_state['user_id'] = login_id
                            st.rerun()

                    except Exception as e:
                        st.error(f"로그인 처리 중 오류 발생: {e}")

            st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem; margin-bottom: 10px;'>아직 사용자 등록을 하지 않으셨나요?</p>", unsafe_allow_html=True)
            if st.button("시스템 첫 접속하기 (사용자 등록)", type="secondary", use_container_width=True):
                st.session_state['view_mode'] = 'register'
                st.rerun()

    # ---------------- [B] 시스템 첫 접속 (사용자 등록) 화면 ----------------
    elif st.session_state['view_mode'] == 'register':
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div style='text-align: center; color: #1e293b; font-size: 1.8rem; font-weight: 700; margin-bottom: 10px;'>시스템 첫 접속</div>", unsafe_allow_html=True)
            
            path_choice = st.radio(
                "사용자 선택",
                ["네이버프리미엄콘텐츠 구독자", "네이버스토어 구매자"],
                horizontal=True
            )

            new_id = st.text_input("사용할 아이디", key=f"reg_id_{uuid.uuid4().hex[:8]}")
            new_pw = st.text_input("사용할 비밀번호", type="password", key=f"reg_pw_{uuid.uuid4().hex[:8]}")

            # 팝업 가림 원천 차단용 공간
            st.markdown("<div style='height: 110px;'></div>", unsafe_allow_html=True)

            master_key = ""
            proof_info = ""

            if path_choice == "네이버프리미엄콘텐츠 구독자":
                master_key = st.text_input("파로스대입랩 공지 마스터 키", key="np_key_v2")
            else:
                proof_info = st.text_input("네이버스토어 주문번호", key="store_order_v2")

            st.markdown("<p style='color: #64748b; font-size: 0.9rem; text-align: center; margin-top: 15px;'>첫 등록을 완료한 이후부터 바로 아이디와 비밀번호로 로그인하여 시스템을 사용하실 수 있습니다.</p>", unsafe_allow_html=True)

            if st.button("등록 완료 및 접속", type="primary", use_container_width=True):
                if not new_id or not new_pw:
                    st.warning("아이디와 비밀번호를 모두 입력해주세요.")
                elif path_choice == "네이버프리미엄콘텐츠 구독자" and not master_key:
                    st.warning("파로스대입랩 공지 마스터 키를 입력해주세요.")
                elif path_choice == "네이버스토어 구매자" and not proof_info:
                    st.warning("네이버스토어 주문번호를 입력해주세요.")
                else:
                    try:
                        sheet = init_connection()
                        records = sheet.get_all_records()

                        for record in records:
                            if str(record.get('아이디')) == new_id:
                                st.error("이미 사용 중인 아이디입니다. 다른 아이디를 입력해주세요.")
                                return

                        days_to_add = 15 if path_choice == "네이버프리미엄콘텐츠 구독자" else 30
                        
                        if path_choice == "네이버프리미엄콘텐츠 구독자":
                            if datetime.now() > datetime(2026, 11, 13):
                                st.error("⚠️ 네프콘 15일 무료 체험 기간이 종료되었습니다.")
                                return

                        expire_date = (datetime.now() + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
                        
                        if 'device_token' not in st.session_state:
                            st.session_state['device_token'] = str(uuid.uuid4())
                        current_device = st.session_state['device_token']

                        save_master_key = master_key if path_choice == "네이버프리미엄콘텐츠 구독자" else ""
                        save_proof_info = proof_info if path_choice == "네이버스토어 구매자" else ""

                        new_row = [new_id, new_pw, save_master_key, save_proof_info, expire_date, current_device, "", ""]
                        sheet.append_row(new_row)

                        st.success("🎉 등록이 완료되었습니다! 로그인 화면으로 돌아갑니다.")
                        st.session_state['view_mode'] = 'login'
                        st.rerun()

                    except Exception as e:
                        st.error(f"처리 중 오류 발생: {e}")

            if st.button("돌아가기 (로그인 화면)", type="secondary", use_container_width=True):
                st.session_state['view_mode'] = 'login'
                st.rerun()

# --- [4] 메인 면접 앱 실행 영역 ---
def main_app():
    st.sidebar.title("👤 회원 정보")
    st.sidebar.write(f"접속 계정: **{st.session_state.get('user_id')}**님")
    if st.sidebar.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.rerun()

    st.sidebar.markdown("---")
    
    st.title("🎓 파로스 서류 기반 모의면접 트레이너 v1.5")
    st.write("선생님께서 기존에 다듬어두신 모의면접 및 제미나이 AI 질문 추출, TTS 음성 출력 코드가 이 아래로 매끄럽게 이어집니다.")
    st.info("여기에 기존의 생기부/자소서 업로드 및 면접 질문 생성 기능 코드를 붙여넣어 사용하시면 됩니다.")

# --- [5] 세션 상태 관리 및 앱 구동 흐름 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    auth_screen()
else:
    main_app()
