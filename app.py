import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import json
import os
import uuid

# --- [1] 페이지 기본 설정 ---
st.set_page_config(
    page_title="파로스 서류 기반 모의면접 트레이너 1.5",
    page_icon="🎓",
    layout="wide"
)

# --- [디자인 스타일 CSS] ---
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 25px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .brand-section {
        text-align: center;
        margin-bottom: 30px;
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

# --- [3] 로그인 및 시스템 첫 접속 화면 처리 ---
def auth_screen():
    # 상단 고급 배너
    st.markdown("""
        <div class="main-header">
            <h2 style='margin: 0; font-size: 1.8rem;'>파로스 서류 기반 모의면접 트레이너</h2>
            <p style='margin: 5px 0 0 0; color: #94a3b8; font-size: 0.95rem;'>맞춤형 면접 질문 추출 및 실전 구술 음성 지원 시스템</p>
        </div>
    """, unsafe_allow_html=True)

    # 브랜드 로고 및 네프콘 링크 영역
    st.markdown("""
        <div class="brand-section">
            <span style="font-size: 1.5rem;">🚨</span><br>
            <b style="color: #1e293b; font-size: 1.1rem;">네이버프리미엄콘텐츠 파로스대입랩</b><br>
            <a href="https://contents.premium.naver.com/pharoslab/jinhak" target="_blank" style="color: #2563eb; text-decoration: none; font-size: 0.9rem;">https://contents.premium.naver.com/pharoslab/jinhak</a>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # 탭 용어 정립: [시스템 첫 접속] 및 [기존 계정 로그인]
    tab1, tab2 = st.tabs(["🚀 시스템 첫 접속", "🔑 기존 계정 로그인"])

    # [탭1] 시스템 첫 접속 (최초 1회 등록)
    with tab1:
        st.subheader("신규 이용권 등록 및 시스템 첫 접속")
        
        track_choice = st.radio(
            "이용 경로를 선택해주세요:",
            [
                "🛒 [트랙 1] 네이버스토어 단품 구매자 (30일 이용권)",
                "📰 [트랙 2] 네이버프리미엄콘텐츠 구독자 (15일 무료 체험)"
            ]
        )

        st.markdown("---")
        new_id = st.text_input("사용할 아이디 설정", key="new_id")
        new_pw = st.text_input("사용할 비밀번호 설정", type="password", key="new_pw")

        if "트랙 1" in track_choice:
            master_key = st.text_input("스토어 마스터 키", key="store_key", placeholder="스토어 안내 페이지의 키 입력")
            proof_info = st.text_input("네이버스토어 주문번호", key="store_order", placeholder="결제하신 주문번호 입력")
        else:
            master_key = st.text_input("네프콘 공용 마스터 키 (패스워드)", key="np_key", placeholder="네프콘 게시글 내 패스워드 입력")
            proof_info = st.text_input("본인의 네이버 아이디", key="np_id", placeholder="구독 인증용 네이버 아이디 입력")

        st.markdown("<p style='color: #64748b; font-size: 0.85em;'>※ 최초 1회 등록 후에는 우측 [기존 계정 로그인] 탭을 이용해 간편하게 접속하실 수 있습니다.</p>", unsafe_allow_html=True)

        if st.button("시스템 첫 접속 완료", type="primary"):
            if not new_id or not new_pw or not master_key or not proof_info:
                st.warning("모든 항목을 빠짐없이 입력해주세요.")
                return

            try:
                sheet = init_connection()
                records = sheet.get_all_records()

                for record in records:
                    if str(record.get('아이디')) == new_id:
                        st.error("이미 사용 중인 아이디입니다. 다른 아이디를 입력해주세요.")
                        return

                days_to_add = 0
                if "트랙 1" in track_choice:
                    days_to_add = 30
                else:
                    transition_date = datetime(2026, 11, 13)
                    if datetime.now() > transition_date:
                        st.error("⚠️ 네프콘 15일 무료 체험 기간이 종료되었습니다. 네이버스토어에서 단품 구매 후 이용해 주세요.")
                        return
                    days_to_add = 15

                expire_date = (datetime.now() + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
                
                if 'device_token' not in st.session_state:
                    st.session_state['device_token'] = str(uuid.uuid4())
                current_device = st.session_state['device_token']

                new_row = [new_id, new_pw, master_key, proof_info, expire_date, current_device, "", ""]
                sheet.append_row(new_row)

                st.success(f"🎉 시스템 첫 접속 등록이 완료되었습니다! (이용 기간: {days_to_add}일, 만료일: {expire_date}) 상단의 [기존 계정 로그인] 탭에서 로그인해 주세요.")

            except Exception as e:
                st.error(f"처리 중 오류 발생: {e}")

    # [탭2] 로그인 로직
    with tab2:
        st.subheader("등록된 계정으로 로그인")
        login_id = st.text_input("아이디", key="login_id")
        login_pw = st.text_input("비밀번호", type="password", key="login_pw")

        if st.button("로그인", type="primary"):
            if not login_id or not login_pw:
                st.error("아이디와 비밀번호를 모두 입력해주세요.")
                return

            try:
                sheet = init_connection()
                if not sheet:
                    st.error("데이터베이스 연결에 실패했습니다. 관리자에게 문의하세요.")
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
                        st.error("⚠️ 이용 기간이 만료되었습니다. 스토어 또는 네프콘에서 기간 연장 후 이용해 주세요.")
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
                            st.error("🚫 동시 접속 기기 초과! (최대 3대까지만 접속 가능합니다.)")
                            return
                    else:
                        st.success("로그인 성공!")

                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = login_id
                    st.rerun()

            except Exception as e:
                st.error(f"로그인 처리 중 오류 발생: {e}")

# --- [4] 메인 면접 앱 실행 영역 (로그인 완료 시) ---
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
