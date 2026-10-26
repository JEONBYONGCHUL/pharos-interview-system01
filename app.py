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

# --- [3] 로그인 및 회원가입 화면 처리 ---
def auth_screen():
    st.markdown("<h2 style='text-align: center;'>🎓 파로스 서류 기반 모의면접 트레이너 v1.5</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>네이버스토어 및 네이버프리미엄콘텐츠 구독자 전용 통합 시스템</p>", unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2 = st.tabs(["🔑 로그인", "📝 신규 회원가입 (이용권 등록)"])

    # [탭1] 로그인 로직
    with tab1:
        st.subheader("기존 계정 로그인")
        login_id = st.text_input("아이디", key="login_id")
        login_pw = st.text_input("비밀번호", type="password", key="login_pw")

        if st.button("로그인하기", type="primary"):
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
                        row_idx = idx + 2 # 엑셀 행 번호 (1행은 헤더)
                        break

                if not user_row:
                    st.error("존재하지 않는 아이디입니다.")
                elif str(user_row.get('비밀번호')) != login_pw:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    # 기간 만료 체크
                    expire_date = datetime.strptime(str(user_row.get('만료일')), "%Y-%m-%d")
                    if datetime.now() > expire_date:
                        st.error("⚠️ 이용 기간이 만료되었습니다. 스토어 또는 네프콘에서 기간 연장 후 이용해 주세요.")
                        return

                    # 기기 3대 제한 체크
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

    # [탭2] 회원가입 로직 (투 트랙 분기)
    with tab2:
        st.subheader("신규 이용권 등록 및 회원가입")
        
        # 트랙 선택 라디오 버튼
        track_choice = st.radio(
            "이용 경로를 선택해주세요:",
            [
                "🛒 [트랙 1] 네이버스토어 단품 구매자 (30일 이용권)",
                "📰 [트랙 2] 네이버프리미엄콘텐츠 구독자 (15일 무료 체험)"
            ]
        )

        st.markdown("---")
        new_id = st.text_input("사용할 아이디", key="new_id")
        new_pw = st.text_input("사용할 비밀번호", type="password", key="new_pw")

        if "트랙 1" in track_choice:
            master_key = st.text_input("스토어 마스터 키", key="store_key", placeholder="스토어 안내 페이지의 키 입력")
            proof_info = st.text_input("네이버스토어 주문번호", key="store_order", placeholder="결제하신 주문번호 입력")
        else:
            master_key = st.text_input("네프콘 공용 마스터 키 (패스워드)", key="np_key", placeholder="네프콘 게시글 내 패스워드 입력")
            proof_info = st.text_input("본인의 네이버 아이디", key="np_id", placeholder="구독 인증용 네이버 아이디 입력")

        st.markdown("<p style='color: red; font-size: 0.85em;'>※ 타인의 정보를 도용하여 가입할 경우, 사전 통보 없이 계정이 영구 정지됩니다.</p>", unsafe_allow_html=True)

        if st.button("회원가입 완료", type="primary"):
            if not new_id or not new_pw or not master_key or not proof_info:
                st.warning("모든 항목을 빠짐없이 입력해주세요.")
                return

            try:
                sheet = init_connection()
                records = sheet.get_all_records()

                # 아이디 중복 체크
                for record in records:
                    if str(record.get('아이디')) == new_id:
                        st.error("이미 사용 중인 아이디입니다. 다른 아이디를 입력해주세요.")
                        return

                # 트랙별 기간 산정 로직
                days_to_add = 0
                if "트랙 1" in track_choice:
                    days_to_add = 30  # 스토어 구매자 30일
                else:
                    # 11월 13일 이후 체험 기간 종료 체크 예시 (필요시 날짜 제어)
                    transition_date = datetime(2026, 11, 13)
                    if datetime.now() > transition_date:
                        st.error("⚠️ 네프콘 15일 무료 체험 기간이 종료되었습니다. 네이버스토어에서 단품 구매 후 이용해 주세요.")
                        return
                    days_to_add = 15  # 네프콘 구독자 15일

                expire_date = (datetime.now() + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
                
                if 'device_token' not in st.session_state:
                    st.session_state['device_token'] = str(uuid.uuid4())
                current_device = st.session_state['device_token']

                new_row = [new_id, new_pw, master_key, proof_info, expire_date, current_device, "", ""]
                sheet.append_row(new_row)

                st.success(f"🎉 회원가입이 완료되었습니다! (이용 기간: {days_to_add}일, 만료일: {expire_date}) 로그인 탭에서 로그인해 주세요.")

            except Exception as e:
                st.error(f"회원가입 처리 중 오류 발생: {e}")

# --- [4] 메인 면접 앱 실행 영역 (로그인 완료 시) ---
def main_app():
    st.sidebar.title("👤 회원 정보")
    st.sidebar.write(f"접속 계정: **{st.session_state.get('user_id')}**님")
    if st.sidebar.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.rerun()

    st.sidebar.markdown("---")
    
    # --- [기존 모의면접 앱 핵심 기능 영역] ---
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
