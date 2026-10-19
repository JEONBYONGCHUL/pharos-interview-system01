import os, json, urllib.request, urllib.error
import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(
    page_title="교과 탐구 및 프로젝트 활동 모의 면접",
    page_icon="logo.png",  # 파로스 로고
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 스타일링 CSS
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
* { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; }

/* 상하단 여백 최소화 */
.block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
[data-testid="stSidebar"] > div:first-child { padding-top: 2rem !important; }

/* 🚫 하단 광고 및 플로팅 버튼 완벽 차단 */
footer, 
[data-testid="stFooter"], 
[data-testid="stBottom"],
[data-testid="stAppDeployButton"],
[data-testid="manage-app-button"],
.viewerBadge_container, 
.viewerBadge_link, 
a[href^="https://streamlit.io"],
div[class^="viewerBadge"] {
    visibility: hidden !important; 
    display: none !important;
}

/* 💡 상단 헤더는 투명하게 유지하되, Share/GitHub 로고 등 툴바 액션만 핀셋 제거 (점 3개는 생존) */
[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
}
[data-testid="stToolbarActions"], .stDeployButton, [data-testid="stDeployButton"] {
    display: none !important;
}

/* 헤더 배너 스타일 */
.header-box { 
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
    padding: 24px 15px; 
    border-radius: 14px; 
    color: white; 
    margin-bottom: 16px; 
    text-align: center; 
    box-shadow: 0 8px 20px -4px rgba(15, 23, 42, 0.25); 
}
.b-title { 
    font-size: clamp(16px, 4vw, 30px); 
    font-weight: 800; 
    letter-spacing: -0.04em; 
    color: #f8fafc; 
    margin: 0; 
    line-height: 1.3; 
    white-space: nowrap; 
    overflow: hidden; 
    text-overflow: ellipsis; 
}
.b-sub { 
    font-size: clamp(11.5px, 2.5vw, 15px); 
    color: #94a3b8; 
    margin-top: 8px; 
    margin-bottom: 0px; 
    word-break: keep-all; 
}

/* 네프콘 채널 링크 박스 스타일 */
.brand-blog-center { 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    gap: 14px; 
    padding: 10px 0 16px 0; 
    margin-bottom: 16px; 
    border-bottom: 1px solid #e2e8f0; 
}
.logo-box { width: 44px; height: 40px; display: flex; align-items: center; justify-content: center; }
.brand-info-box { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; }
.brand-title-text { font-size: 15px; font-weight: 800; color: #0f172a; }
.brand-link-text { font-size: 13.5px; color: #0284c7 !important; text-decoration: none !important; font-weight: 600; }
.brand-link-text:hover { color: #0369a1 !important; text-decoration: underline !important; }

/* 사이드바 스타일 */
[data-testid="stSidebar"] { background-color: #f8fafc; border-right: 1px solid #e2e8f0; }
.side-title { 
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
    color: white; 
    padding: 14px; 
    border-radius: 10px; 
    text-align: center; 
    font-weight: 800; 
    font-size: 15.5px; 
    margin-bottom: 16px; 
}

/* 실행 버튼 및 결과 카드 */
div.stButton > button { 
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important; 
    color: white !important; 
    border: none !important; 
    border-radius: 10px !important; 
    padding: 14px 24px !important; 
    font-size: 16px !important; 
    font-weight: 800 !important; 
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important; 
}
div.stButton > button:hover { 
    background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important; 
    box-shadow: 0 6px 18px rgba(2, 132, 199, 0.45) !important; 
}
.card { 
    background: white; 
    border: 1px solid #e2e8f0; 
    border-left: 5px solid #0284c7; 
    border-radius: 12px; 
    padding: 20px 22px; 
    margin-bottom: 14px; 
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04); 
}
.q-title { font-size: 17px; font-weight: 700; color: #0f172a; margin: 10px 0; line-height: 1.5; word-break: keep-all; }
.guide { 
    background: #f0fdf4; 
    border: 1px solid #bbf7d0; 
    color: #166534; 
    padding: 10px 14px; 
    border-radius: 8px; 
    font-size: 13.5px; 
    font-weight: 600; 
    margin-top: 10px; 
    word-break: keep-all; 
}

/* 비밀번호 인증 박스 스타일 */
.auth-box {
    background: white;
    border: 1px solid #e2e8f0;
    border-top: 5px solid #0f172a;
    border-radius: 12px;
    padding: 30px;
    margin: 40px auto;
    max-width: 400px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    text-align: center;
}
.auth-title { font-size: 20px; font-weight: 800; color: #0f172a; margin-bottom: 10px; }
.auth-desc { font-size: 14px; color: #64748b; margin-bottom: 20px; word-break: keep-all; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# 파로스 등대 SVG 심볼
svg_logo = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 155" width="100%" height="100%">
<polygon points="12,24 64,42 64,50 12,34" fill="#831843"/>
<polygon points="12,56 64,56 64,64 12,68" fill="#52525b"/>
<polygon points="168,24 116,42 116,50 168,34" fill="#52525b"/>
<polygon points="168,56 116,56 116,64 168,68" fill="#831843"/>
<polygon points="90,10 87,22 93,22" fill="#831843"/>
<path d="M72,36 Q90,22 108,36 Z" fill="#831843"/>
<rect x="75" y="36" width="30" height="16" fill="#fff" stroke="#831843" stroke-width="2.5"/>
<line x1="82" y1="36" x2="82" y2="52" stroke="#831843" stroke-width="2"/>
<line x1="90" y1="36" x2="90" y2="52" stroke="#831843" stroke-width="2"/>
<line x1="98" y1="36" x2="98" y2="52" stroke="#831843" stroke-width="2"/>
<polygon points="70,52 110,52 106,58 74,58" fill="#831843"/>
<polygon points="73,59 107,59 116,134 64,134" fill="#831843"/>
<polygon points="96,59 105,59 74,102 69,96" fill="#fff" opacity="0.95"/>
<polygon points="107,92 114,103 81,134 71,134" fill="#fff" opacity="0.95"/>
<rect x="36" y="134" width="108" height="6" rx="2" fill="#831843"/>
</svg>"""

# 3. 메인 배너
st.markdown("""
<div class="header-box">
    <div class="b-title">교과 탐구 및 프로젝트 활동 모의 면접</div>
    <div class="b-sub">교과 탐구 및 프로젝트 기반 맞춤형 면접 질문 추출 및 실전 구술 음성 지원 시스템</div>
</div>
""", unsafe_allow_html=True)

# 4. 네이버 프리미엄콘텐츠 채널 링크 (주소 수정)
st.markdown(f"""
<div class="brand-blog-center">
    <div class="logo-box">{svg_logo}</div>
    <div class="brand-info-box">
        <span class="brand-title-text">네이버 프리미엄콘텐츠 파로스대입랩</span>
        <a class="brand-link-text" href="https://contents.premium.naver.com/pharoslab/jinhak" target="_blank">https://contents.premium.naver.com/pharoslab/jinhak</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# 💡 [보안] 프리미엄 콘텐츠 구독자용 입장 코드 인증 로직
# ==========================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # 인증되지 않은 사용자에게 보여줄 로그인 창
    st.markdown("""
    <div class="auth-box">
        <div class="auth-title">🔒 프리미엄 시스템 입장</div>
        <div class="auth-desc">네이버 프리미엄콘텐츠 파로스대입랩 구독자 전용 서비스입니다.<br>안내받으신 <b>입장 코드</b>를 입력해 주세요.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        access_code = st.text_input("입장 코드 입력", type="password", label_visibility="collapsed", placeholder="입장 코드를 입력하세요")
        if st.button("시스템 접속하기", use_container_width=True):
            if access_code == "pharos2027":
                st.session_state["authenticated"] = True
                st.rerun()  # 인증 성공 시 페이지 새로고침하여 본 화면 진입
            else:
                st.error("❌ 올바르지 않은 코드입니다. 다시 확인해 주세요.")
    
    # 인증 실패 시 아래쪽 본문 코드가 실행되지 않도록 완전히 차단
    st.stop()
# ==========================================================

# 5. 관련 법령 준수 안내 배너
st.info(
    "🔒 **관련 법령 준수 안내**\n\n"
    "본 시스템은 **「초·중등교육법」 제25조의2**에 따라 **학교생활기록부 원문(PDF / 세특 기재문)의 수집·업로드를 전면 차단**하며, "
    "수험생 본인의 **탐구 활동 요약 메모만을 기반으로 모의면접 질문을 지원합니다.**"
)

# API 키 직접 연동
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("⚠️ Streamlit Secrets에 GEMINI_API_KEY가 등록되지 않았습니다.")
    st.stop()

def sanitize_text(text):
    import re
    t = text
    t = re.sub(r'[가-힣]{2,10}(고등학교|여고|남고|외고|과고|예고|체고|마이스터고|공고|상고|고)', "[OO고등학교]", t)
    t = re.sub(r'\b\d{6}[-\s]?[1-4]\d{6}\b', '[주민번호 마스킹]', t)
    t = re.sub(r'\b(19\d{2}|20\d{2})[.-년\s]+(0?[1-9]|1[0-2])[.-월\s]+(0?[1-9]|[12]\d|3[01])일?\b', '[생년월일 마스킹]', t)
    t = re.sub(r'01[016789][-\s]?\d{3,4}[-\s]?\d{4}', '[연락처 마스킹]', t)
    t = re.sub(r'\b(아버지|어머니|부모님|부친|모친|형|누나|오빠|언니|동생|외조부|조부|외조모|조모|삼촌|이모|고모)\b', "[가족관계]", t)
    return t

def call_gemini(prompt, count, diff):
    diff_desc = {"하": "기초 사실 확인", "중": "탐구 과정 및 문제해결", "상": "심화 이론 및 메커니즘"}.get(diff, "")
    sys_prompt = f"""당신은 대한민국 명문 대학 대입 학생부종합전형 수석 입학사정관입니다.
제공된 학생 본인의 교과 탐구 및 프로젝트 활동 요약 텍스트를 분석하여 [{diff} 난이도: {diff_desc}]에 부합하는 면접 질문 총 {count}문항을 생성하세요.

반드시 마크다운 백틱 없이 순수 JSON 포맷으로만 응답하세요:
{{
  "major": "지원 전공",
  "difficulty": "{diff}",
  "sections": [
    {{
      "category": "활동 영역 구분 (예: 교과 연계 심화 탐구, 전공 프로젝트, 융합 활동 등)",
      "questions": [
        {{
          "type": "문항 유형",
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
        "contents": [{"role": "user", "parts": [{"text": f"{sys_prompt}\n\n{prompt}"}]}],
        "generationConfig": {"temperature": 0.7}
    }
    encoded_body = json.dumps(body).encode("utf-8")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={API_KEY}"
    
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
        alert('🚫 현재 열려있는 창(카카오톡, 네이버 앱 등)에서는 보안상 음성 재생을 지원하지 않습니다.\\n\\n💡 화면 우측 하단이나 우측 상단의 [메뉴(점 3개)]를 눌러서 [다른 브라우저로 열기(크롬, 사파리)]를 선택하시면 음성 지원을 완벽하게 이용하실 수 있습니다!'); 
        return; 
    }}
    window.speechSynthesis.cancel();
    let u = new SpeechSynthesisUtterance({clean});
    u.lang = 'ko-KR'; u.rate = 0.93;
    let v = window.speechSynthesis.getVoices().find(x => x.lang && x.lang.includes('ko'));
    if (v) u.voice = v;
    u.onstart = () => {{ document.getElementById('b_{q_id}').style.background = '#475569'; document.getElementById('s_{q_id}').innerText = '낭독 중...'; }};
    u.onend = () => {{ document.getElementById('b_{q_id}').style.background = 'linear-gradient(180deg,#0284c7,#0369a1)'; document.getElementById('s_{q_id}').innerText = ''; }};
    window.speechSynthesis.speak(u);
}};
</script>"""
    components.html(html, height=46)

# 6. 사이드바 
with st.sidebar:
    st.markdown('<div class="side-title">⚙️ 모의 면접 조건 설정</div>', unsafe_allow_html=True)
    target_major = st.text_input("지원 희망 전공/학과", placeholder="예: 컴퓨터공학과, 의예과")
    q_sel = st.selectbox("추출 면접 문항 수", ["10문항", "5문항", "3문항"], index=2)
    q_count = int(q_sel.replace("문항", ""))
    diff_sel = st.selectbox("평가 난이도", ["하 (기초 사실 확인)", "중 (탐구/문제해결)", "상 (심화 학술이론)"], index=0)
    difficulty = diff_sel[0]

# 7. 메인 입력 영역
st.markdown("### 본인의 교과 탐구 및 프로젝트 활동 요약 입력")

st.caption("✅ **안심하고 사용하세요!** 본 모의 면접 시스템은 완전 휘발성 구조로 설계되어, 입력하신 모든 데이터는 서버에 일절 저장되지 않고 즉시 파기됩니다.")

placeholder_content = """본인의 핵심 탐구 주제와 경험을 요약해 주세요.
(※ 초·중등교육법 제25조의2에 따라 학생부 원문 복사 입력은 제한됩니다)"""

input_text = st.text_area(
    label="활동 요약 텍스트 입력",
    label_visibility="collapsed",
    height=200,
    placeholder=placeholder_content
)

# 8. 질문 추출 실행 버튼
if st.button("🚀 면접 질문 추출하기", use_container_width=True):
    if not input_text.strip():
        st.warning("⚠️ 면접 대비를 원하는 탐구 활동 요약 내용을 입력해 주세요.")
    else:
        with st.spinner("모의 면접관께서 탐구 활동 내용 및 전공 심화 개념을 정밀 분석 중입니다..."):
            sanitized = sanitize_text(input_text)
            prompt = f"지원 전공: {target_major or '미지정'}\n\n[탐구 활동 요약]\n{sanitized}"
            try:
                res = call_gemini(prompt, q_count, difficulty)
                st.success(f"🎉 총 {q_count}문항 추출 완료 (난이도: {difficulty})")
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
