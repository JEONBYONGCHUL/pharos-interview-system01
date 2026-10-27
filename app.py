import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import json
import os
import time
import re
import urllib.request
import urllib.error
import streamlit.components.v1 as components

# --- [1] 페이지 기본 설정 ---
st.set_page_config(
    page_title="파로스 서류 기반 모의면접 트레이너",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- [2] UI 디자인 및 스타일 정의 ---
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; word-break: keep-all; }
    
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 2rem !important; }
    
    [data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; }
    footer { visibility: hidden !important; }

    .header-box { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px 15px; border-radius: 14px; color: white; margin-bottom: 10px; text-align: center; box-shadow: 0 8px 20px -4px rgba(15, 23, 42, 0.25); display: flex; flex-direction: column; justify-content: center; align-items: center; }
    .b-title { font-size: clamp(16px, 4vw, 26px); font-weight: 800; letter-spacing: -0.04em; margin: 0; line-height: 1.3; white-space: nowrap; }
    .b-sub { font-size: clamp(11.5px, 2.5vw, 15px); color: #94a3b8; margin-top: 6px; margin-bottom: 0; }
    
    .brand-blog-center { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 5px 0 10px 0; margin-bottom: 10px; border-bottom: 1px solid #e2e8f0; text-align: center; }
    .logo-box { width: 45px; height: 40px; display: flex; align-items: center; justify-content: center; }
    .brand-info-box { display: flex; flex-direction: column; align-items: center; gap: 3px; width: 100%; padding: 0 5px; }
    .brand-title-text { font-size: 14.5px; font-weight: 800; color: #0f172a; line-height: 1.2; }
    .brand-link-text { font-size: clamp(10px, 3vw, 13px); color: #0284c7 !important; text-decoration: none !important; font-weight: 600; line-height: 1.3; letter-spacing: -0.5px; }

    .side-title { background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: white; padding: 14px; border-radius: 10px; text-align: center; font-weight: 800; font-size: 15.5px; margin-bottom: 16px; }

    div.stButton > button[kind="primary"] { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important; color: white !important; border: none !important; border-radius: 10px !important; padding: 10px 24px !important; font-size: 16px !important; font-weight: 800 !important; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important; margin-top: 5px; }
    div.stButton > button[kind="primary"]:hover { background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important; box-shadow: 0 6px 18px rgba(2, 132, 199, 0.45) !important; }
    
    .card { background: white; border: 1px solid #e2e8f0; border-left: 5px solid #0284c7; border-radius: 12px; padding: 20px 22px; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04); }
    .q-title { font-size: 17px; font-weight: 700; color: #0f172a; margin: 10px 0; line-height: 1.5; }
    .guide { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 10px 14px; border-radius: 8px; font-size: 13.5px; font-weight: 600; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

svg_logo = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 155" width="100%" height="100%">
<polygon points="12,24 64,42 64,50 12,34" fill="#831843"/><polygon points="12,56 64,56 64,64 12,68" fill="#52525b"/>
<polygon points="168,24 116,42 116,50 168,34" fill="#52525b"/><polygon points="168,56 116,56 116,64 168,68" fill="#831843"/>
<polygon points="90,10 87,22 93,22" fill="#831843"/><path d="M72,36 Q90,22 108,36 Z" fill="#831843"/>
<rect x="75" y="36" width="30" height="16" fill="#fff" stroke="#831843" stroke-width="2.5"/>
<line x1="82" y1="36" x2="82" y2="52" stroke="#831843" stroke-width="2"/><line x1="90" y1="36" x2="90" y2="52" stroke="#831843" stroke-width="2"/>
<line x1="98" y1="36" x2="98" y2="52" stroke="#831843" stroke-width="2"/><polygon points="70,52 110,52 106,58 74,58" fill="#831843"/>
<polygon points="73,59 107,59 116,134 64,134" fill="#831843"/><polygon points="96,59 105,59 74,102 69,96" fill="#fff" opacity="0.95"/>
<polygon points="107,92 114,103 81,134 71,134" fill="#fff" opacity="0.95"/><rect x="36" y="134" width="108" height="6" rx="2" fill="#831843"/>
</svg>"""

# --- [3] 구글 시트 DB 연결 함수 ---
def init_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds, secret_data = None, os.environ.get("GCP_JSON")
    
    if not secret_data:
        try:
            if "GCP_JSON" in st.secrets: secret_data = st.secrets["GCP_JSON"]
        except Exception: pass
            
    if secret_data:
        try:
            creds_dict = json.loads(secret_data) if isinstance(secret_data, str) else dict(secret_data)
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
                    except Exception: continue 
        except Exception: pass
                    
    if creds is None:
        st.error("🚨 [인증 파일 누락] 서버 환경변수(GCP_JSON) 또는 로컬 폴더에 구글 인증 JSON 파일이 없습니다.")
        return None 
        
    try:
        client = gspread.authorize(creds)
        return client.open("파로스모의면접1.5회원DB").sheet1
    except Exception as e:
        st.error(f"🚨 [연결 오류] {e}")
        return None

# --- [4] 로그인 및 첫 접속 인증 화면 (순수 계정 인증 방식) ---
def auth_screen():
    components.html(
        """<script>
        const doc = window.parent.document;
        doc.querySelectorAll('input').forEach(input => { input.setAttribute('autocomplete', 'new-password'); input.setAttribute('data-lpignore', 'true'); });
        doc.querySelectorAll('input[type="password"]').forEach(pw => {
            pw.setAttribute('readonly', 'true');
            pw.addEventListener('focus', function() { this.removeAttribute('readonly'); });
            pw.addEventListener('blur', function() { this.setAttribute('readonly', 'true'); });
        });
        </script>""", height=0, width=0
    )

    st.markdown('<div class="header-box"><div class="b-title">파로스 서류 기반 모의면접 트레이너</div><div class="b-sub">맞춤형 면접 질문 추출 및 실전 구술 음성 지원 시스템</div></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="brand-blog-center">
        <div class="logo-box">{svg_logo}</div>
        <div class="brand-info-box">
            <span class="brand-title-text">네이버프리미엄콘텐츠 파로스대입랩</span>
            <a class="brand-link-text" href="https://contents.premium.naver.com/pharoslab/jinhak" target="_blank">https://contents.premium.naver.com/pharoslab/jinhak</a>
        </div>
    </div>
    <hr style="margin: 5px 0 15px 0; border: none; border-top: 1px solid #e2e8f0;">
    """, unsafe_allow_html=True)

    if 'view_mode' not in st.session_state: st.session_state['view_mode'] = 'login'

    if st.session_state['view_mode'] == 'login':
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_id = st.text_input("아이디", key="login_id")
            login_pw = st.text_input("비밀번호", placeholder="비밀번호 입력", key="login_pw")
            show_login_pw = st.checkbox(" 비밀번호 보기", key="chk_login_pw")
            
            if not show_login_pw: st.markdown('<style>input[placeholder="비밀번호 입력"] { -webkit-text-security: disc !important; }</style>', unsafe_allow_html=True)
            
            if st.button("로그인", type="primary", use_container_width=True):
                if not login_id or not login_pw: st.error("아이디와 비밀번호를 모두 입력해주세요.")
                else:
                    try:
                        sheet = init_connection()
                        if not sheet: return
                        records = sheet.get_all_records()
                        user_row = None

                        for idx, record in enumerate(records):
                            if str(record.get('아이디')) == login_id:
                                user_row = record
                                break

                        if not user_row: st.error("존재하지 않는 아이디입니다.")
                        elif str(user_row.get('비밀번호')) != login_pw: st.error("비밀번호가 일치하지 않습니다.")
                        else:
                            expire_date = datetime.strptime(str(user_row.get('만료일')), "%Y-%m-%d")
                            if datetime.now() > expire_date:
                                st.error("⚠️ 이용 기간이 만료되었습니다.")
                                return

                            st.success("로그인 성공!")
                            st.session_state['logged_in'] = True
                            st.session_state['user_id'] = login_id
                            st.rerun()
                    except Exception as e: st.error(f"로그인 처리 중 오류 발생: {e}")

            st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
            if st.button("시스템 첫 접속하기 (사용자 등록)", type="secondary", use_container_width=True):
                st.session_state['view_mode'] = 'register'
                st.rerun()

    elif st.session_state['view_mode'] == 'register':
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div style='text-align: center; color: #1e293b; font-size: 1.8rem; font-weight: 700; margin-bottom: 10px;'>시스템 첫 접속</div>", unsafe_allow_html=True)
            
            path_choice = st.selectbox("사용자 선택", ["네이버스토어 구매자", "네이버프리미엄콘텐츠 구독자"])
            new_id = st.text_input("사용할 아이디", key="reg_id")
            new_pw = st.text_input("사용할 비밀번호", placeholder="비밀번호 설정", key="reg_pw")
            show_reg_pw = st.checkbox(" 비밀번호 보기", key="chk_reg_pw")
            
            if not show_reg_pw: st.markdown('<style>input[placeholder="비밀번호 설정"] { -webkit-text-security: disc !important; }</style>', unsafe_allow_html=True)

            master_key, proof_info = "", ""
            
            if path_choice == "네이버프리미엄콘텐츠 구독자":
                master_key = st.text_input("공지 마스터 키", key="np_key_v2")
                proof_info = st.text_input("네이버 아이디", key="np_id_v2")
            else:
                master_key = st.text_input("앱 마스터 키", key="store_key_v2")
                proof_info = st.text_input("네이버스토어 주문번호", key="store_order_v2")

            if st.button("등록 완료 및 접속", type="primary", use_container_width=True):
                if not new_id or not new_pw or not master_key or not proof_info:
                    st.warning("모든 항목을 입력해 주세요.")
                elif path_choice == "네이버프리미엄콘텐츠 구독자" and master_key != "pharosjinhak2027":
                    st.error("❌ 공지 마스터 키가 일치하지 않습니다.")
                elif path_choice == "네이버스토어 구매자" and master_key != "pharosstore2027sucess":
                    st.error("❌ 앱 마스터 키가 일치하지 않습니다.")
                else:
                    try:
                        sheet = init_connection()
                        if not sheet: return
                        records = sheet.get_all_records()
                        for record in records:
                            if str(record.get('아이디')) == new_id:
                                st.error("이미 사용 중인 아이디입니다.")
                                return

                        days_to_add = 15 if path_choice == "네이버프리미엄콘텐츠 구독자" else 30
                        expire_date = (datetime.now() + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
                        
                        sheet.append_row([new_id, new_pw, master_key, proof_info, expire_date, "", "", "", ""])
                        st.success(" 등록이 완료되었습니다! 로그인 화면으로 돌아갑니다.")
                        st.session_state['view_mode'] = 'login'
                        st.rerun()
                    except Exception as e: st.error(f"처리 중 오류 발생: {e}")

            if st.button("돌아가기 (로그인 화면)", type="secondary", use_container_width=True):
                st.session_state['view_mode'] = 'login'
                st.rerun()

# --- [5] AI 데이터 처리 함수 및 프롬프트 영역 ---
def sanitize_text(text):
    t = text
    t = re.sub(r'[가-힣]{2,10}(고등학교|여고|남고|외고|과고|예고|체고|마이스터고|공고|상고|고)', "[OO고등학교]", t)
    t = re.sub(r'\b\d{6}[-\s]?[1-4]\d{6}\b', '[주민번호 마스킹]', t)
    t = re.sub(r'\b(19\d{2}|20\d{2})[.-년\s]+(0?[1-9]|1[0-2])[.-월\s]+(0?[1-9]|[12]\d|3[01])일?\b', '[생년월일 마스킹]', t)
    t = re.sub(r'01[016789][-\s]?\d{3,4}[-\s]?\d{4}', '[연락처 마스킹]', t)
    t = re.sub(r'\b(아버지|어머니|부모님|부친|모친|형|누나|오빠|언니|동생|외조부|조부|외조모|조모|삼촌|이모|고모)\b', "[가족관계]", t)
    return t

def call_gemini(prompt, count, diff, api_key):
    diff_prompts = {
        "하": "기초 사실 확인 및 역량 균형 평가 (주요 초점: 진로 희망 변경 이유, 가장 의미 있었던 과목, 서류 내 기억에 남는 활동 등 팩트와 경험 위주의 개방형 질문 포함. ★ '학업역량', '진로역량', '공동체역량' 세 가지 측면의 질문을 고르게 균형 있게 혼합하여 출제할 것)",
        "중": "탐구 과정/문제해결 및 학업·진로 중심 평가 (주요 초점: 프로젝트 내 구체적 역할과 수행 내용, 갈등 극복 경험 등 상황 대처 위주의 질문 포함. ★ '공동체역량'보다 '학업역량'과 '진로역량'에 관련된 질문의 비중을 높여서 출제할 것)",
        "상": "심화 한계 극복, 포부 및 압박 심층 평가 (주요 초점: 탐구 중 발생한 학술적/기술적 한계와 극복 과정, 전공 심화 지식, 대학 입학 후 학업 계획 및 미래 포부 등. ★ '학업역량'과 '진로역량' 비중을 압도적으로 높게 두고, 학생의 활동 요약 내용을 꼬리질문 하듯 매우 심층적이고 예리하게 파고드는 압박형 질문으로 출제할 것)"
    }
    diff_desc = diff_prompts.get(diff, "")
    current_time_seed = time.time()
    
    sys_prompt = f"""당신은 대한민국 명문 대학 대입 학생부종합전형 수석 입학사정관입니다.
제공된 학생 본인의 교과 탐구 및 프로젝트 활동 요약 텍스트를 분석하여 [{diff} 난이도]에 부합하는 면접 질문 총 {count}문항을 생성하세요.

[난이도별 핵심 평가 요소: {diff_desc}]
- 중요 지침 1: 생성되는 질문 중 최소 1~2문항 이상은 위의 [난이도별 핵심 평가 요소]를 묻는 개방형/인성 면접 질문으로 구성하고, 서류 기반 질문과 자연스럽게 믹스하세요.
- 중요 지침 2: 학생이 여러 번 연습할 수 있도록 매 요청마다 전혀 다른 앵글의 변형된 질문을 생성하세요. (System Random Seed 적용됨)
- 중요 지침 3: 아무리 난이도가 높은 질문이라도, 고등학생이 즉각적으로 이해할 수 있도록 어려운 학술 용어나 한자어 사용을 피하고, 부드럽고 쉬운 일상적인 구어체로 질문을 구성하세요.
- 중요 지침 4: 질문의 형태를 다채롭게 구성하세요. 핵심을 하나만 묻는 '단일 질문'과, "A를 설명해보고, 그것을 바탕으로 B를 어떻게 해결했는지 말씀해주세요."처럼 두 가지를 동시에 묻는 '복합 질문(2-part question)'을 적절한 비율로 자연스럽게 섞어서 출제하세요.

반드시 마크다운 백틱 없이 순수 JSON 포맷으로만 응답하세요:
{{
  "major": "지원 전공",
  "difficulty": "{diff}",
  "sections": [
    {{
      "category": "활동 영역 구분 (예: 교과 연계 심화 탐구, 전공 프로젝트, 인성 및 공동체 활동 등)",
      "questions": [
        {{
          "type": "문항 유형 (심층 면접, 인성 면접, 꼬리 질문 등)",
          "source_quote": "요약문 기반 핵심 활동 근거",
          "question": "면접 질문 본문",
          "intent": "면접관 출제 의도",
          "high_score_guide": "고득점 답변 가이드 및 필수 포함 키워드"
        }}
      ]
    }}
  ]
}}"""
    
    body = {
        "contents": [{"role": "user", "parts": [{"text": f"{sys_prompt}\n\n{prompt}\n\n[System 난수: {current_time_seed}]"}]}],
        "generationConfig": {"temperature": 0.85}
    }
    encoded_body = json.dumps(body).encode("utf-8")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
    req = urllib.request.Request(url, data=encoded_body, headers={"Content-Type": "application/json"}, method="POST")
    
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if "candidates" not in res:
                raise Exception("생성된 응답이 없습니다.")
            txt = res["candidates"][0]["content"]["parts"][0]["text"].strip()
            if txt.startswith("```json"): txt = txt[7:]
            if txt.startswith("```"): txt = txt[3:]
            if txt.endswith("```"): txt = txt[:-3]
            return json.loads(txt.strip())
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        raise Exception(f"HTTP {e.code} 에러: {err_msg}")
    except Exception as e:
        raise Exception(f"API 요청 실패: {str(e)}")

def render_tts(text, q_id):
    clean = json.dumps(text, ensure_ascii=False)
    html = f"""<button id="b_{q_id}" style="background:linear-gradient(180deg,#0284c7,#0369a1);color:white;border:none;border-radius:6px;padding:7px 15px;font-size:13px;font-weight:700;cursor:pointer;box-shadow:0 2px 5px rgba(2,132,199,0.25);">🔊 음성으로 질문 듣기</button>
<span id="s_{q_id}" style="font-size:12px;color:#64748b;margin-left:10px;"></span>
<script>
document.getElementById('b_{q_id}').onclick = function() {{
    if (!('speechSynthesis' in window)) {{ 
        alert(' 카카오톡, 네이버 등 앱 내부 브라우저에서는 음성 재생이 차단될 수 있습니다.\\n\\n화면 우측 하단(또는 상단)의 [ ⠇] 또는 [ ≡ ] 메뉴 기호를 눌러 반드시 \\'다른 브라우저로 열기(사파리, 크롬 등)\\'를 선택해 주세요.'); 
        return; 
    }}
    window.speechSynthesis.cancel();
    let u = new SpeechSynthesisUtterance({clean});
    u.lang = 'ko-KR'; 
    u.rate = 0.93; 
    u.pitch = 0.75; 
    
    let voices = window.speechSynthesis.getVoices();
    let koVoices = voices.filter(x => x.lang && x.lang.includes('ko'));
    let maleVoice = koVoices.find(x => x.name.toLowerCase().includes('male') || x.name.includes('남성') || x.name.toLowerCase().includes('injoon'));
    
    if (maleVoice) {{
        u.voice = maleVoice;
        u.pitch = 0.9; 
    }} else if (koVoices.length > 0) {{
        u.voice = koVoices[0]; 
    }}

    u.onstart = () => {{ document.getElementById('b_{q_id}').style.background = '#475569'; document.getElementById('s_{q_id}').innerText = '낭독 중...'; }};
    u.onend = () => {{ document.getElementById('b_{q_id}').style.background = 'linear-gradient(180deg,#0284c7,#0369a1)'; document.getElementById('s_{q_id}').innerText = ''; }};
    
    u.onerror = (e) => {{
        if (e.error !== 'interrupted') {{
            alert(' 카카오톡, 네이버 등 앱 내부 브라우저에서는 음성 재생이 차단될 수 있습니다.\\n\\n화면 우측 하단(또는 상단)의 [ ⠇] 또는 [ ≡ ] 메뉴 기호를 눌러 반드시 \\'다른 브라우저로 열기(사파리, 크롬 등)\\'를 선택해 주세요.');
            document.getElementById('b_{q_id}').style.background = 'linear-gradient(180deg,#0284c7,#0369a1)'; 
            document.getElementById('s_{q_id}').innerText = '';
        }}
    }};
    
    window.speechSynthesis.speak(u);
}};
</script>"""
    components.html(html, height=46)


# --- [6] 메인 면접 앱 실행 영역 ---
def main_app():
    st.sidebar.markdown(f"<div style='background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 20px;'><p style='margin: 0; color: #475569; font-weight: 600;'>👤 접속 계정: <b>{st.session_state.get('user_id')}</b>님</p></div>", unsafe_allow_html=True)
    if st.sidebar.button("로그아웃", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.rerun()

    st.sidebar.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #cbd5e1;'>", unsafe_allow_html=True)
    
    st.sidebar.markdown('<div class="side-title">⚙️ 모의 면접 조건 설정</div>', unsafe_allow_html=True)
    target_major = st.sidebar.text_input("지원 모집단위 및 희망 전공", placeholder="예: 경영학부, 컴퓨터공학과")
    q_sel = st.sidebar.selectbox("추출 면접 문항 수", ["5문항", "10문항", "15문항"], index=0)
    q_count = int(q_sel.replace("문항", ""))
    
    diff_sel = st.sidebar.selectbox("평가 난이도", ["하 (기본사실확인)", "중 (탐구문제해결)", "상 (심화학업역량,압박)"], index=0)
    difficulty = diff_sel[0]
    
    st.sidebar.markdown("---")
    include_intro = st.sidebar.checkbox(" 지원 동기 (시작 공통 문항) 포함", value=True, help="체크 시 '왜 해당 모집단위/전공에 지원했는가?' 문항이 첫 번째로 자동 추가됩니다.")
    include_closing = st.sidebar.checkbox(" 마지막 할 말 (마무리 공통 문항) 포함", value=True, help="체크 시 면접을 마무리하는 '마지막으로 하고 싶은 말' 문항이 맨 끝에 자동 추가됩니다.")

    st.markdown('<div class="header-box"><div class="b-title">파로스 서류 기반 모의면접 트레이너</div><div class="b-sub">맞춤형 면접 질문 추출 및 실전 구술 음성 지원 시스템</div></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="brand-blog-center">
        <div class="logo-box">{svg_logo}</div>
        <div class="brand-info-box">
            <span class="brand-title-text">네이버프리미엄콘텐츠 파로스대입랩</span>
            <a class="brand-link-text" href="https://contents.premium.naver.com/pharoslab/jinhak" target="_blank">https://contents.premium.naver.com/pharoslab/jinhak</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #eff6ff; border-radius: 8px; padding: 20px; margin-bottom: 24px; border: 1px solid #bfdbfe;">
        <div style="font-weight: 800; margin-bottom: 10px; font-size: 16px; color: #1e3a8a; text-align: center;">관련 법령 준수 안내</div>
        <div style="color: #1e3a8a; font-size: 14.5px; line-height: 1.6; text-align: left; word-break: keep-all;">
            본 시스템은 「초·중등교육법」 제25조의2에 유의하여 학교생활기록부를 취득하지 않습니다. 학교생활기록부의 수집·업로드를 전면 차단하며, 수험생 본인의 탐구 활동 등 내용 입력 사항을 기반으로 모의 면접 질문을 지원합니다.
        </div>
    </div>
    <div style="text-align: center; margin-top: 5px; margin-bottom: 5px;">
        <h3 style='font-size: clamp(20px, 5vw, 26px); font-weight: 800; color: #0f172a; margin: 0; white-space: nowrap;'>본인 탐구 활동 등 내용 입력</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("✅ **안심하고 사용하세요!** 본 모의 면접 시스템은 완전 휘발성 구조로 설계되어, 입력하신 모든 내용은 서버에 일절 저장되지 않고 즉시 파기됩니다.")
    
    input_text = st.text_area("활동 요약 텍스트 입력", placeholder="본인의 탐구 활동 등 내용을 입력해 주세요.", height=200, label_visibility="collapsed")
    
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    if st.button(" 면접 질문 추출하기", type="primary", use_container_width=True):
        if not input_text.strip():
            st.warning("⚠️ 면접 대비를 원하는 탐구 활동 요약 내용을 입력해 주세요.")
        else:
            api_key = os.environ.get("GEMINI_API_KEY") or (st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else None)
            
            if not api_key:
                st.error("🚨 환경변수에 GEMINI_API_KEY가 설정되어 있지 않습니다.")
            else:
                with st.spinner("모의 면접관께서 기록 사항을 정밀 분석 중입니다..."):
                    sanitized = sanitize_text(input_text)
                    prompt = f"지원 모집단위 및 희망 전공: {target_major or '미지정'}\n\n[탐구 활동 요약]\n{sanitized}"
                    
                    try:
                        res = call_gemini(prompt, q_count, difficulty, api_key)
                        
                        if "sections" not in res: res["sections"] = []
                        
                        if include_intro:
                            major_text = target_major.strip() if target_major.strip() else "해당 모집단위"
                            res["sections"].insert(0, {
                                "category": "기본 소양 및 지원 동기 (공통 필수)",
                                "questions": [{
                                    "type": "공통/인성 면접",
                                    "source_quote": "대입 면접 공통 필수 평가 항목",
                                    "question": f"{major_text}에 지원하게 된 동기가 무엇인지 편하게 말씀해 주시고, 입학하게 된다면 어떤 학업 계획을 가지고 있는지도 함께 설명해 주세요.",
                                    "intent": "지원 모집단위 및 전공에 대한 관심도, 학업에 대한 열정 및 진로 계획의 구체성 확인",
                                    "high_score_guide": "단순한 흥미나 학교의 명성을 언급하기보다는, 본인의 기존 탐구 활동이나 관심 분야를 해당 전공의 커리큘럼(또는 대학의 인재상)과 연결지어 논리적이고 구체적으로 답변하는 것이 중요합니다."
                                }]
                            })

                        if include_closing:
                            res["sections"].append({
                                "category": "최종 어필 및 마무리 (공통 필수)",
                                "questions": [{
                                    "type": "공통/인성 면접",
                                    "source_quote": "대입 면접 마무리 공통 평가 항목",
                                    "question": "마지막으로 면접관에게 꼭 하고 싶은 말이나, 미처 다 보여주지 못한 본인의 장점이 있다면 편하게 말씀해 주세요.",
                                    "intent": "지원자의 최종적인 입학 의지, 자기 어필 능력, 그리고 면접에 임하는 태도와 진정성 확인",
                                    "high_score_guide": "준비해온 답변을 단순히 암기해서 말하기보다는, 오늘 면접에서의 아쉬웠던 점을 보완하거나 이 대학/학과에 진학하고자 하는 진정성을 진솔하게 표현하는 것이 좋습니다."
                                }]
                            })

                        st.success(f" 면접 문항 추출이 완료되었습니다. (난이도: {difficulty})")
                        st.markdown("---")
                        
                        q_num = 1
                        for sec in res.get("sections", []):
                            st.markdown(f"#### 📁 {sec.get('category')}")
                            for item in sec.get("questions", []):
                                st.markdown(f"""
                                <div class="card">
                                    <span style="background:#e0f2fe;color:#0369a1;font-size:12px;font-weight:700;padding:3px 10px;border-radius:20px;">[{item.get('type', '심층 면접')}] · 난이도 {difficulty}</span>
                                    <div class="q-title">Q{q_num}. {item.get('question')}</div>
                                    <div style="font-size:13.5px;color:#475569;margin-bottom:5px;">📌 <b>활동 근거:</b> <i>"{item.get('source_quote')}"</i></div>
                                    <div style="font-size:13.5px;color:#475569;margin-bottom:5px;">🎯 <b>출제 의도:</b> {item.get('intent')}</div>
                                    <div class="guide">💡 <b>고득점 답변 가이드:</b> {item.get('high_score_guide')}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                render_tts(item.get('question'), f"q_{q_num}")
                                q_num += 1
                                
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {str(e)}")

# --- [7] 세션 상태 관리 및 앱 구동 흐름 ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']: auth_screen()
else: main_app()
