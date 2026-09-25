import os, json, urllib.request, urllib.error
import streamlit as st
import streamlit.components.v1 as components
from pypdf import PdfReader

# 1. 페이지 레이아웃 및 설정
st.set_page_config(
    page_title="2028 대입 학생부 기반 모의 면접",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 스타일링 CSS
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
* { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; }

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem !important;
}

/* 상단 메인 타이틀 배너 (가운데 정렬) */
.header-box {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    padding: 28px 20px;
    border-radius: 14px;
    color: white;
    margin-bottom: 16px;
    text-align: center;
    box-shadow: 0 8px 20px -4px rgba(15, 23, 42, 0.25);
}
.b-title {
    font-size: clamp(22px, 3.2vw, 34px);
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #f8fafc;
    margin: 0;
    line-height: 1.2;
}
.b-sub {
    font-size: clamp(13px, 1.3vw, 15px);
    color: #94a3b8;
    margin-top: 8px;
    margin-bottom: 0px;
}

/* 파로스 블로그 바 (로고 + 블로그명 + 링크 가운데 정렬) */
.brand-blog-center {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    padding: 12px 0 18px 0;
    margin-bottom: 22px;
    border-bottom: 1px solid #e2e8f0;
}
.logo-box {
    width: 46px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.brand-info-box {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
}
.brand-title-text {
    font-size: 15px;
    font-weight: 800;
    color: #0f172a;
}
.brand-link-text {
    font-size: 13.5px;
    color: #0284c7 !important;
    text-decoration: none !important;
    font-weight: 600;
}
.brand-link-text:hover {
    color: #0369a1 !important;
    text-decoration: underline !important;
}

/* 사이드바 스타일링 */
[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
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
.priv-box {
    background: #f1f5f9;
    padding: 14px;
    border-radius: 10px;
    border-left: 4px solid #0284c7;
    margin-top: 25px;
    font-size: 12px;
    color: #475569;
    line-height: 1.5;
    border: 1px solid #cbd5e1;
}

/* 실행 버튼 */
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

/* 질문 카드 디자인 */
.card {
    background: white;
    border: 1px solid #e2e8f0;
    border-left: 5px solid #0284c7;
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 14px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
}
.q-title {
    font-size: 17px;
    font-weight: 700;
    color: #0f172a;
    margin: 10px 0;
    line-height: 1.5;
}
.guide {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 13.5px;
    font-weight: 600;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# 파로스 등대 심볼 벡터 SVG
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

# 3. 메인 타이틀 배너 (가운데 정렬)
st.markdown("""
<div class="header-box">
    <div class="b-title">2028 대입 학생부 기반 모의 면접</div>
    <div class="b-sub">학생부 기반 맞춤형 면접 질문 추출 및 실전 구술 음성 지원 시스템</div>
</div>
""", unsafe_allow_html=True)

# 4. 파로스 블로그 바 (가운데 정렬, 꺾쇠 없는 단일 링크)
st.markdown(f"""
<div class="brand-blog-center">
    <div class="logo-box">{svg_logo}</div>
    <div class="brand-info-box">
        <span class="brand-title-text">파로스대입랩 네이버블로그</span>
        <a class="brand-link-text" href="https://blog.naver.com/pharoslab" target="_blank" rel="noopener noreferrer">https://blog.naver.com/pharoslab</a>
    </div>
</div>
""", unsafe_allow_html=True)

# API 키 로드 (기본 키 보장)
raw_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6IS_OUgZ873T4q4PCU7grpIhRjgeUuRc2VQE6NEQ34BEg"))
GEMINI_API_KEY = str(raw_key).strip().strip("'").strip('"')

def extract_pdf(f):
    reader = PdfReader(f)
    pages = []
    for p in reader.pages:
        txt = p.extract_text()
        if txt:
            pages.append(txt)
    return "\n".join(pages)

def sanitize_text(text, name=""):
    t = text
    if name and len(name.strip()) >= 2:
        t = t.replace(name.strip(), "[OO학생]")
    import re
    t = re.sub(r'[가-힣]{2,10}(고등학교|여고|남고|외고|과고|예고|체고|마이스터고|공고|상고|고)', "[OO고등학교]", t)
    t = re.sub(r'\b\d{6}[-\s]?[1-4]\d{6}\b', '[주민번호 마스킹]', t)
    t = re.sub(r'\b(19\d{2}|20\d{2})[.-년\s]+(0?[1-9]|1[0-2])[.-월\s]+(0?[1-9]|[12]\d|3[01])일?\b', '[생년월일 마스킹]', t)
    t = re.sub(r'01[016789][-\s]?\d{3,4}[-\s]?\d{4}', '[연락처 마스킹]', t)
    t = re.sub(r'\b(아버지|어머니|부모님|부친|모친|형|누나|오빠|언니|동생|외조부|조부|외조모|조모|삼촌|이모|고모)\b', "[가족관계]", t)
    return t

def call_gemini(prompt, count, diff):
    diff_desc = {"하": "기초 사실 확인", "중": "탐구 과정 및 문제해결", "상": "심화 이론 및 메커니즘"}.get(diff, "")
    
    sys_prompt = f"""당신은 대한민국 명문 대학 대입 학생부종합전형 수석 입학사정관입니다.
제공된 학생부 텍스트를 분석하여 [{diff} 난이도: {diff_desc}]에 부합하는 면접 질문 총 {count}문항을 생성하세요.

반드시 마크다운 백틱 없이 순수 JSON 포맷으로만 응답하세요:
{{
  "major": "지원 전공",
  "difficulty": "{diff}",
  "sections": [
    {{
      "category": "영역 구분명 (예: 창의적 체험활동 진로·자율활동, 교과 세부능력및특기사항 등)",
      "questions": [
        {{
          "type": "문항 유형",
          "source_quote": "학생부 근거 문맥 인용",
          "question": "면접 질문 본문",
          "intent": "면접관 출제 의도",
          "high_score_guide": "고득점 답변 가이드 및 필수 포함 키워드"
        }}
      ]
    }}
  ]
}}"""

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{sys_prompt}\n\n{prompt}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7
        }
    }
    encoded_body = json.dumps(body).encode("utf-8")
    
    # AQ. 유료 키를 위한 멀티 인증 헤더 및 URL 조합
    auth_configs = [
        # 방식 1: URL 쿼리 파라미터 (Google Cloud API 키 표준)
        {"url_suffix": f"?key={GEMINI_API_KEY}", "headers": {"Content-Type": "application/json"}},
        # 방식 2: Bearer 토큰 (Google Cloud 서비스 계정/OAuth 표준)
        {"url_suffix": "", "headers": {"Content-Type": "application/json", "Authorization": f"Bearer {GEMINI_API_KEY}"}},
        # 방식 3: x-goog-api-key 헤더
        {"url_suffix": "", "headers": {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}}
    ]

    base_models = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    ]

    last_error = ""

    for cfg in auth_configs:
        for base_url in base_models:
            full_url = base_url + cfg["url_suffix"]
            try:
                req = urllib.request.Request(full_url, data=encoded_body, headers=cfg["headers"], method="POST")
                with urllib.request.urlopen(req) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    txt = res["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if txt.startswith("```json"): txt = txt[7:]
                    if txt.startswith("```"): txt = txt[3:]
                    if txt.endswith("```"): txt = txt[:-3]
                    return json.loads(txt.strip())
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8")
                last_error = f"{e.code} - {err_body}"
                continue
            except Exception as e:
                last_error = str(e)
                continue

    raise Exception(f"API 호출 실패: {last_error}")

def render_tts(text, q_id):
    clean = json.dumps(text, ensure_ascii=False)
    html = f"""<button id="b_{q_id}" style="background:linear-gradient(180deg,#0284c7,#0369a1);color:white;border:none;border-radius:6px;padding:7px 15px;font-size:13px;font-weight:700;cursor:pointer;box-shadow:0 2px 5px rgba(2,132,199,0.25);">🔊 음성으로 질문 듣기</button>
<span id="s_{q_id}" style="font-size:12px;color:#64748b;margin-left:10px;"></span>
<script>
document.getElementById('b_{q_id}').onclick = function() {{
    if (!('speechSynthesis' in window)) {{ alert('음성 재생을 지원하지 않는 브라우저입니다.'); return; }}
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

# 5. 사이드바
with st.sidebar:
    st.markdown('<div class="side-title">⚙️ 모의 면접 조건 설정</div>', unsafe_allow_html=True)
    student_name = st.text_input("학생 실명 (마스킹용)", placeholder="홍길동 (선택)")
    target_major = st.text_input("지원 희망 전공/학과", placeholder="예: 컴퓨터공학과, 의예과")
    q_sel = st.selectbox("추출 면접 문항 수", ["10문항", "5문항", "3문항"], index=2)
    q_count = int(q_sel.replace("문항", ""))
    diff_sel = st.selectbox("평가 난이도", ["하 (기초 사실 확인)", "중 (탐구/문제해결)", "상 (심화 학술이론)"], index=0)
    difficulty = diff_sel[0]
    st.markdown('<div class="priv-box"><b>🔒 개인정보 안심 처리</b><br>인적사항, 고교명, 가족관계 등 대입 블라인드 항목은 자동 마스킹 처리되니 안심하셔도 됩니다.</div>', unsafe_allow_html=True)

# 6. 메인 탭
tab1, tab2 = st.tabs(["✍️ [방법 1] 학생부 텍스트 직접 입력", "📂 [방법 2] 학생부 PDF 업로드"])
input_text = ""

with tab1:
    txt_input = st.text_area("학생부 내용을 복사해 붙여넣으세요", height=220, placeholder="과세특, 창체, 행특 내용을 이곳에 붙여넣으세요...")
    if txt_input:
        input_text = txt_input

with tab2:
    pdf_file = st.file_uploader("학생부 PDF 파일을 올려주세요", type=["pdf"])
    if pdf_file:
        with st.spinner("PDF 텍스트를 추출하는 중입니다..."):
            input_text = extract_pdf(pdf_file)
            st.success("✅ 학생부 PDF 텍스트 추출 완료")

# 7. 면접 질문 추출 버튼
if st.button("🚀 면접 질문 추출하기", use_container_width=True):
    if not input_text.strip():
        st.warning("⚠️ 학생부 내용을 입력하거나 PDF를 올려주세요.")
    else:
        with st.spinner("사정관 AI가 학생부 탐구 내용 및 교과 개념을 정밀 분석 중입니다..."):
            sanitized = sanitize_text(input_text, student_name)
            prompt = f"지원 전공: {target_major or '미지정'}\n\n[학생부 원문]\n{sanitized}"
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
                            <div style="font-size:13.5px;color:#475569;margin-bottom:5px;">📌 <b>학생부 근거:</b> <i>"{item.get('source_quote')}"</i></div>
                            <div style="font-size:13.5px;color:#475569;margin-bottom:5px;">🎯 <b>출제 의도:</b> {item.get('intent')}</div>
                            <div class="guide">💡 <b>고득점 답변 가이드:</b> {item.get('high_score_guide')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        render_tts(item.get('question'), f"q_{q_num}")
                        q_num += 1
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
