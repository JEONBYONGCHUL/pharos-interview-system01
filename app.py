import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import json
import os
import uuid
import base64
import streamlit.components.v1 as components

# --- [1] 페이지 기본 설정 ---
st.set_page_config(
    page_title="파로스 서류 기반 모의면접 트레이너 1.5",
    page_icon="logo.png" if os.path.exists("logo.png") else "🎓",
    layout="wide"
)

# --- [2] UI 디자인 (로그인 및 시스템 공통 디자인 동결) ---
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { 
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; 
        word-break: keep-all; 
    }
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    
    .header-box { 
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
        padding: 30px 15px !important; 
        border-radius: 12px; 
        color: white; 
        margin-bottom: 15px; 
        text-align: center; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .header-box div {
        margin: 0 !important;
        padding: 0 !important;
    }
    .b-title { 
        font-size: clamp(18px, 4.5vw, 26px); 
        font-weight: 800; 
        letter-spacing: -0.04em; 
        margin: 0 !important; 
        line-height: 1.4 !important; 
        white-space: nowrap; 
        color: white !important; 
    }
    .b-sub { 
        font-size: clamp(11.5px, 2.8vw, 15px); 
        color: #94a3b8; 
        margin-top: 8px !important; 
        margin-bottom: 0 !important; 
        line-height: 1.4 !important; 
    }
    
    .brand-blog-center { 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center; 
        gap: 8px; 
        padding: 5px 0 10px 0; 
        margin-bottom: 15px; 
        text-align: center; 
    }
    .brand-title-text { 
        font-size: clamp(14px, 3.5vw, 17px); 
        font-weight: 800; 
        color: #1e293b; 
        line-height: 1.2; 
    }
    .brand-link-text { 
        font-size: clamp(11px, 2.5vw, 14px); 
        color: #2563eb !important; 
        text-decoration: none !important; 
        font-weight: 600; 
        line-height: 1.3; 
        letter-spacing: -0.5px; 
        word-break: break-all; 
    }

    div.stButton > button[kind="primary"], div.stButton > button[kind="secondary"] { 
        background-color: #1e293b !important; 
        color: white !important; 
        border: none !important; 
        border-radius: 6px !important; 
        font-weight: bold !important; 
        padding: 0.5rem 1rem !important; 
        margin-top: 5px !important; 
    }
    div.stButton > button:hover { background-color: #0f172a !important; }
</style>
""", unsafe_allow_html=True)

# --- [3] 구글 시트 DB 연결 함수 (동결) ---
def init_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = None
    
    secret_data = os.environ.get("GCP_JSON")
    
    if not secret_data:
        try:
            if "GCP_JSON" in st.secrets:
                secret_data = st.secrets["GCP_JSON"]
        except Exception:
            pass
            
    if secret_data:
        try:
            if isinstance(secret_data, str):
                creds_dict = json.loads(secret_data)
            else:
                creds_dict = dict(secret_data)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        except Exception as e:
            st.error(f"🚨 [JSON 파싱 오류] 등록하신 GCP_JSON 데이터의 형태가 잘못되었습니다: {e}")
            return None
        
    if creds is None:
        try:
            for f in os.listdir('.'):
                if f.endswith('.json'):
                    try:
                        with open(f, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            if "private_key" in data and "client_email" in data:
                                creds = ServiceAccountCredentials.from_json_keyfile_name(f, scope)
                                break 
                    except Exception:
                        continue 
        except Exception:
            pass
                    
    if creds is None:
        st.error("🚨 [인증 파일 누락] 서버 환경변수(GCP_JSON) 또는 로컬 폴더에 구글 인증 JSON 파일이 없습니다.")
        return None 
        
    try:
        client = gspread.authorize(creds)
        sheet = client.open("파로스모의면접1.5회원DB").sheet1
        return sheet
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("🚨 [시트 권한 누락] '파로스모의면접1.5회원DB' 시트를 찾을 수 없습니다. 구글 시트 설정에서 편집자 권한을 주셨는지 확인해주세요.")
        return None
    except Exception as e:
        st.error(f"🚨 [알 수 없는 연결 오류] {e}")
        return None

# --- [4] 로그인 및 첫 접속 라우팅 (비밀번호 및 마스터키 검증 완벽 동결) ---
def auth_screen():
    components.html(
        """
        <script>
        const doc = window.parent.document;
        const inputs = doc.querySelectorAll('input');
        inputs.forEach(input => {
            input.setAttribute('autocomplete', 'new-password');
            input.setAttribute('data-lpignore', 'true');
        });
        const pwInputs = doc.querySelectorAll('input[type="password"]');
        pwInputs.forEach(pw => {
            pw.setAttribute('readonly', 'true');
            pw.addEventListener('focus', function() { this.removeAttribute('readonly'); });
            pw.addEventListener('blur', function() { this.setAttribute('readonly', 'true'); });
        });
        </script>
        """, height=0, width=0
    )

    st.markdown('<div class="header-box"><div class="b-title">파로스 서류 기반 모의면접 트레이너</div><div class="b-sub">맞춤형 면접 질문 추출 및 실전 구술 음성 지원 시스템</div></div>', unsafe_allow_html=True)

    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f'''
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin: 5px 0 10px 0;">
                <img src="data:image/png;base64,{img_b64}" style="width: 70px; height: auto;" />
            </div>
            ''',
            unsafe_allow_html=True
        )
    
    st.markdown("""
    <div class="brand-blog-center">
        <span class="brand-title-text">네이버프리미엄콘텐츠 파로스대입랩</span>
        <a class="brand-link-text" href="https://contents.premium.naver.com/pharoslab/jinhak" target="_blank">https://contents.premium.naver.com/pharoslab/jinhak</a>
    </div>
    <hr style="margin: 5px 0 15px 0; border: none; border-top: 1px solid #e2e8f0;">
    """, unsafe_allow_html=True)

    if 'view_mode' not in st.session_state:
        st.session_state['view_mode'] = 'login'

    # ---------------- [A] 로그인 화면 ----------------
    if st.session_state['view_mode'] == 'login':
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_id = st.text_input("아이디", key="login_id")
            login_pw = st.text_input("비밀번호", placeholder="비밀번호 입력", key="login_pw")
            show_login_pw = st.checkbox("👁️ 비밀번호 보기", key="chk_login_pw")
            
            if not show_login_pw:
                st.markdown('<style>input[placeholder="비밀번호 입력"] { -webkit-text-security: disc !important; }</style>', unsafe_allow_html=True)
            
            if st.button("로그인", type="primary", use_container_width=True):
                if not login_id or not login_pw:
                    st.error("아이디와 비밀번호를 모두 입력해주세요.")
                else:
                    try:
                        sheet = init_connection()
                        if not sheet:
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
            
            path_choice = st.selectbox("사용자 선택", ["네이버프리미엄콘텐츠 구독자", "네이버스토어 구매자"])
            new_id = st.text_input("사용할 아이디", key="reg_id")
            new_pw = st.text_input("사용할 비밀번호", placeholder="비밀번호 설정", key="reg_pw")
            show_reg_pw = st.checkbox("👁️ 비밀번호 보기", key="chk_reg_pw")
            
            if not show_reg_pw:
                st.markdown('<style>input[placeholder="비밀번호 설정"] { -webkit-text-security: disc !important; }</style>', unsafe_allow_html=True)

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
                elif path_choice == "네이버프리미엄콘텐츠 구독자" and master_key != "pharosjinhak2027":
                    st.error("❌ 파로스대입랩 공지 마스터 키가 일치하지 않습니다.")
                elif path_choice == "네이버스토어 구매자" and not proof_info:
                    st.warning("네이버스토어 주문번호를 입력해주세요.")
                else:
                    try:
                        sheet = init_connection()
                        if not sheet:
                            return
                            
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

# --- [5] 메인 면접 앱 실행 영역 (1.0 메인화면 완벽 복원 이식) ---
def main_app():
    # 💡 1. 사이드바 복원
    st.sidebar.markdown(f"<div style='background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 20px;'><h3 style='margin:0; color: #1e293b; font-size: 1.2rem;'>👤 회원 정보</h3><p style='margin: 10px 0 0 0; color: #475569;'>접속 계정: <b>{st.session_state.get('user_id')}</b>님</p></div>", unsafe_allow_html=True)
    
    if st.sidebar.button("로그아웃", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.rerun()

    st.sidebar.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #cbd5e1;'>", unsafe_allow_html=True)
    
    # 사이드바 면접 조건 설정
    st.sidebar.markdown("<div style='background-color: #1e293b; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 15px; font-size: 1.05rem;'>⚙️ 모의 면접 조건 설정</div>", unsafe_allow_html=True)
    
    major = st.sidebar.text_input("지원 모집단위 및 희망 전공", placeholder="예: 경영학부, 컴퓨터공학과")
    q_count = st.sidebar.selectbox("추출 면접 문항 수", ["3문항", "4문항", "5문항", "6문항"], index=2)
    difficulty = st.sidebar.selectbox("평가 난이도", ["하 (기초 사실 확인)", "중 (심층 질문)", "상 (꼬리 질문 및 압박)"])
    
    st.sidebar.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    inc_motive = st.sidebar.checkbox("💡 지원 동기 (시작 공통 문항) 포함", value=True)
    inc_last = st.sidebar.checkbox("💡 마지막 할 말 (마무리 공통 문항) 포함", value=True)

    # 💡 2. 메인 바디 복원 (상단 배너 및 로고)
    st.markdown('<div class="header-box"><div class="b-title">파로스 서류 기반 모의면접 트레이너</div><div class="b-sub">맞춤형 면접 질문 추출 및 실전 구술 음성 지원 시스템</div></div>', unsafe_allow_html=True)

    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f'''
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin: 5px 0 10px 0;">
                <img src="data:image/png;base64,{img_b64}" style="width: 70px; height: auto;" />
            </div>
            ''',
            unsafe_allow_html=True
        )
    
    st.markdown("""
    <div class="brand-blog-center">
        <span class="brand-title-text">네이버프리미엄콘텐츠 파로스대입랩</span>
        <a class="brand-link-text" href="https://contents.premium.naver.com/pharoslab/jinhak" target="_blank">https://contents.premium.naver.com/pharoslab/jinhak</a>
    </div>
    <hr style="margin: 5px 0 15px 0; border: none; border-top: 1px solid #e2e8f0;">
    """, unsafe_allow_html=True)

    # 💡 3. 관련 법령 준수 안내 박스 복원
    st.markdown("""
    <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 25px 20px; text-align: center; margin: 20px 0;">
        <div style="color: #1e3a8a; font-weight: 800; font-size: 1.05rem; margin-bottom: 12px;">관련 법령 준수 안내</div>
        <div style="color: #2563eb; font-size: 0.95rem; line-height: 1.6; word-break: keep-all;">
            본 시스템은 「초·중등교육법」 제25조의2에 유의하여 학교생활기록부를 취득하지 않습니다. 학교생활기록부의 수집·업로드를 전면 차단하며, 수험생 본인의 탐구 활동 등 내용 입력 사항을 기반으로 모의 면접 질문을 지원합니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 💡 4. 탐구 활동 입력부 복원
    st.markdown("<h3 style='text-align: center; color: #1e293b; font-weight: 800; margin-top: 40px; margin-bottom: 20px;'>본인 탐구 활동 등 내용 입력</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #10b981; font-size: 0.9rem; margin-bottom: 8px; font-weight: 600;'>✅ 안심하고 사용하세요! 본 모의 면접 시스템은 완전 휘발성 구조로 설계되어, 입력하신 모든 내용은 서버에 일절 저장되지 않고 즉시 파기됩니다.</p>", unsafe_allow_html=True)
    
    activity_text = st.text_area("탐구활동내용", placeholder="본인의 탐구 활동 등 내용을 입력해 주세요.", height=300, label_visibility="collapsed")
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    if st.button("면접 질문 추출하기", type="primary", use_container_width=True):
        if not activity_text:
            st.warning("탐구 활동 내용을 입력해주세요.")
        else:
            st.info("여기에 기존 제미나이(Gemini) AI 연동 코드 및 면접 시작 로직을 이어붙이시면 1.5버전이 최종 완성됩니다.")

# --- [6] 세션 상태 관리 및 앱 구동 흐름 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    auth_screen()
else:
    main_app()
