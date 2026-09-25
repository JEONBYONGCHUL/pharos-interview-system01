import os
import re
import json
import urllib.request
import streamlit as st
import streamlit.components.v1 as components
from pypdf import PdfReader

# 1. 페이지 레이아웃 및 탭 기본 설정
st.set_page_config(
    page_title="2028 대입 학생부 기반 모의 면접",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 고급 브랜드 CSS 스타일링
css_code = """
<style>
@import url('[https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css](https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css)');
* { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif; }

.brand-header-box {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    padding: 30px 32px;
    border-radius: 16px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.brand-title {
    font-size: clamp(20px, 3.2vw, 34px);
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #f8fafc;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 0;
    line-height: 1.2;
}
.brand-subtitle {
    font-size: clamp(13px, 1.4vw, 15px);
    color: #94a3b8;
    font-weight: 400;
    margin-top: 8px;
    margin-bottom: 0px;
}
.brand-meta-box {
    margin-top: 18px;
    padding-top: 16px;
    border-top: 1px solid rgba(148, 163, 184, 0.2);
    display: flex;
    align-items: center;
    gap: 16px;
}
.brand-logo-container {
    width: 68px;
    height: 58px;
    background: #ffffff;
    border-radius: 8px;
    padding: 4px 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
.brand-meta-text {
    display: flex;
    flex-direction: column;
    gap: 3px;
}
.brand-blog-name {
    font-size: 15px;
    font-weight: 800;
    color: #f8fafc;
}
.brand-blog-url {
    font-size: 13.5px;
    color: #ffffff !important;
    text-decoration: underline !important;
    opacity: 0.95;
}
.brand-blog-url:hover {
    opacity: 1.0;
}
[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
.sidebar-header-box {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    padding: 15px;
    border-radius: 10px;
    color: white;
    margin-bottom: 20px;
    text-align: center;
    box-shadow: 0 4px 10px rgba(15, 23, 42, 0.1);
}
.sidebar-header-title {
    font-size: 15.5px;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin: 0;
    color: #f8fafc;
}
.privacy-notice-box {
    background: #f1f5f9;
    border-radius: 10px;
    padding: 14px;
    margin-top: 25px;
    border: 1px solid #cbd5e1;
    border-left: 4px solid #0284c7;
}
.privacy-notice-title {
    font-size: 12.5px;
    font-weight: 800;
    color: #0369a1;
    margin-bottom: 5px;
}
.privacy-notice-desc {
    font-size: 12px;
    color: #475569;
    line-height: 1.5;
    margin: 0;
}
div.stButton > button {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px 24px !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
}
.interview-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 5px solid #0284c7;
    border-radius: 12px;
    padding: 22px 24px;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
}
.badge-type {
    display: inline-block;
    background-color: #e0f2fe;
    color: #0369a1;
    font-size: 12px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
}
.question-title {
    font-size: 17px;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.5;
    margin-bottom: 12px;
}
.meta-row {
    font-size: 13.5px;
    color: #475569;
    margin-bottom: 6px;
    line-height: 1.5;
}
.meta-highlight {
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 13.5px;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 8px;
}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

# 3. 상단 헤더 및 파로스 등대 로고 (선명한 백터 SVG)
header_html = """
<div class="brand-header-box">
    <div class="brand-title">2028 대입 학생부 기반 모의 면접</div>
    <div class="brand-subtitle">학생부 기반 맞춤형 면접 질문 추출 및 실전 구술 음성 지원 시스템</div>
    <div class="brand-meta-box">
        <div class="brand-logo-container">
            <svg xmlns="[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)" viewBox="0 0 180 155" width="100%" height="100%">
                <defs>
                    <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#831843"/>
                        <stop offset="50%" stop-color="#9d174d"/>
                        <stop offset="100%" stop-color="#701a75"/>
                    </linearGradient>
                </defs>
                <polygon points="12,24 64,42 64,50 12,34" fill="url(#purpleGrad)"/>
                <polygon points="12,56 64,56 64,64 12,68" fill="#52525b"/>
                <polygon points="168,24 116,42 116,50 168,34" fill="#52525b"/>
                <polygon points="168,56 116,56 116,64 168,68" fill="url(#purpleGrad)"/>
                <polygon points="90,10 87,22 93,22" fill="#831843"/>
                <path d="M72,36 Q90,22 108,36 Z" fill="url(#purpleGrad)"/>
                <rect x="75" y="36" width="30" height="16" fill="#ffffff" stroke="#831843" stroke-width="2.5"/>
                <line x1="82" y1="36" x2="82" y2="52" stroke="#831843" stroke-width="2"/>
                <line x1="90" y1="36" x2="90" y2="52" stroke="#831843" stroke-width="2"/>
                <line x1="98" y1="36" x2="98" y2="52" stroke="#831843" stroke-width="2"/>
                <polygon points="70,52 110,52 106,58 74,58" fill="#831843"/>
                <polygon points="73,59 107,59 116,134 64,134" fill="url(#purpleGrad)"/>
                <polygon points="96,59 105,59 74,102 69,96" fill="#ffffff" opacity="0.92"/>
                <polygon points="107,92 114,103 81,134 71,134" fill="#ffffff" opacity="0.92"/>
                <rect x="36" y="134" width="108" height="6" rx="2" fill="#831843"/>
            </svg>
        </div>
        <div class="brand-meta-text">
            <span class="brand-blog-name">파로스대입랩 네이버블로그</span>
            <a class="brand-blog-url" href="[http://blog.naver.com/pharoslab](http://blog.naver.com/pharoslab)" target="_blank">[http://blog.naver.com/pharoslab](http://blog.naver.com/pharoslab)</a>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# 4. 서버 API 키 로드
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    extracted = []
    for page in reader.pages:
        txt = page.extract_text()
        if txt:
            extracted.append(txt)
    return "\n".join(extracted)

def sanitize_student_record(text, custom_name=""):
    sanitized = text
    if custom_name and len(custom_name.strip()) >= 2:
        sanitized = re.sub(re.escape(custom_name.strip()), "[OO학생]", sanitized)
    sanitized = re.sub(r'[가-힣]{2,10}(고등학교|여고|남고|외고|과고|예고|체고|마이스터고|공고|상고|고)', "[OO고등학교]", sanitized)
    sanitized = re.sub(r'\b\d{6}[-\s]?[1-4]\d{6}\b', '[주민번호 마스킹]', sanitized)
    sanitized = re.sub(r'\b(19\d{2}|20\d{2})[.-년\s]+(0?[1-9]|1[0-2])[.-월\s]+(0?[1-9]|[12]\d|3[01])일?\b', '[생년월일 마스킹]', sanitized)
    sanitized = re.sub(r'01[016789][-\s]?\d{3,4}[-\s]?\d{4}', '[연락처 마스킹]', sanitized)
    sanitized = re.sub(r'\b(아버지|어머니|부모님|부친|모친|형|누나|오빠|언니|동생|외조부|조부|외조모|조모|삼촌|이모|고모)\b', "[가족관계]", sanitized)
    return sanitized

def build_system_instruction(question_count, difficulty):
    diff_map = {
        "하": "기초 사실 확인형: 활동의 진위 여부와 본인 역할 중심",
        "중": "탐구 과정 및 문제해결형: 인과관계, 오차 극복 논리, 전공 기초 연계 중심",
        "상": "심화 이론 및 메커니즘형: 학술 이론 배경, 원리적 작동 구조, 비판적 반론 중심"
    }
    diff_text = diff_map.get(difficulty, "")

    inst = (
        "당신은 대한민국 명문 대학 대입 학생부종합전형 수석 입학사정관입니다.\n"
        f"제공된 학생부 텍스트를 분석하여 [{difficulty} 난이도: {diff_text}]에 부합하는 면접 질문 총 {question_count}문항을 생성하세요.\n\n"
        "반드시 마크다운 백틱 없이 순수 JSON 포맷으로만 응답하세요:\n"
        "{\n"
        '  "major": "지원 전공",\n'
        f'  "difficulty": "{difficulty}",\n'
        '  "sections": [\n'
        "    {\n"
        '      "category": "영역 구분명 (예: 창의적 체험활동 진로·자율활동, 교과 세부능력및특기사항 등)",\n'
        '      "questions": [\n'
        "        {\n"
        '          "type": "문항 유형",\n'
        '          "source_quote": "학생부 근거 문맥 인용",\n'
        '          "question": "면접 질문 본문",\n'
        '          "intent": "면접관 출제 의도",\n'
        '          "high_score_guide": "고득점 답변 가이드 및 필수 포함 키워드"\n'
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n"
    )
    return inst

def call_gemini_api(prompt, count, diff):
    clean_key = GEMINI_API_KEY.strip()
    url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=){clean_key}"
    headers = {"Content-Type": "application/json"}
    sys_inst = build_system_instruction(count, diff)
    body = {
        "contents": [{"role": "user", "parts": [{"text": f"{sys_inst}\n\n{prompt}"}]}],
        "generationConfig": {"temperature": 0.7, "responseMimeType": "application/json"}
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        t = data['candidates'][0]['content']['parts'][0]['text'].strip()
        if t.startswith("```json"):
            t = t[7:]
        if t.startswith("```"):
            t = t[3:]
        if t.endswith("```"):
            t = t[:-3]
        return json.loads(t.strip())

# 5. 브라우저 음성 재생 (Web Speech API)
def render_tts_button(text, button_id):
    clean_text = json.dumps(text, ensure_ascii=False)
    html_parts = [
        '<div style="margin-bottom: 16px;">',
        f'  <button id="btn_{button_id}" style="display:inline-flex;align-items:center;gap:6px;background:linear-gradient(180deg,#0284c7 0%,#0369a1 100%);color:#ffffff;border:none;border-radius:6px;padding:7px 15px;font-size:13px;font-weight:700;cursor:pointer;box-shadow:0 2px 5px rgba(2,132,199,0.25);">🔊 음성으로 질문 듣기</button>',
        f'  <span id="status_{button_id}" style="font-size:12px;color:#64748b;margin-left:10px;"></span>',
        '</div>',
        '<script>',
        f'const btn_{button_id} = document.getElementById("btn_{button_id}");',
        f'const status_{button_id} = document.getElementById("status_{button_id}");',
        f'const textToRead_{button_id} = {clean_text};',
        f'btn_{button_id}.addEventListener("click", function() {{',
        '  if (!("speechSynthesis" in window)) { alert("사용 중이신 브라우저가 음성 듣기를 지원하지 않습니다."); return; }',
        '  window.speechSynthesis.cancel();',
        f'  const utter = new SpeechSynthesisUtterance(textToRead_{button_id});',
        '  utter.lang = "ko-KR";',
        '  utter.rate = 0.93;',
        '  const voices = window.speechSynthesis.getVoices();',
        '  const koVoice = voices.find(v => v.lang && (v.lang.includes("ko") || v.lang.includes("KO")));',
        '  if (koVoice) { utter.voice = koVoice; }',
        f'  utter.onstart = function() {{ btn_{button_id}.style.background = "#475569"; status_{button_id}.innerText = "낭독 중..."; }};',
        f'  utter.onend = function() {{ btn_{button_id}.style.background = "linear-gradient(180deg, #0284c7 0%, #0369a1 100%)"; status_{button_id}.innerText = ""; }};',
        f'  utter.onerror = function() {{ btn_{button_id}.style.background = "linear-gradient(180deg, #0284c7 0%, #0369a1 100%)"; status_{button_id}.innerText = ""; }};',
        '  window.speechSynthesis.speak(utter);',
        '});',
        'if ("speechSynthesis" in window && window.speechSynthesis.onvoiceschanged !== undefined) {',
        '  window.speechSynthesis.onvoiceschanged = () => { window.speechSynthesis.getVoices(); };',
        '}',
        '</script>'
    ]
    components.html("\n".join(html_parts), height=48)

# 6. 사이드바 - 단일 라인 옵션
with st.sidebar:
    st.markdown('<div class="sidebar-header-box"><div class="sidebar-header-title">⚙️ 모의 면접 조건 설정</div></div>', unsafe_allow_html=True)
    
    student_name = st.text_input("학생 실명 (마스킹용)", placeholder="홍길동 (미입력 가능)")
    target_major = st.text_input("지원 희망 전공/학과", placeholder="예: 신소재공학과, 의예과")
    
    q_choice = st.selectbox("추출 면접 문항 수", ["10문항", "5문항", "3문항"], index=0)
    q_count = int(q_choice.replace("문항", ""))
    
    diff_choice = st.selectbox("평가 난이도", ["중 (탐구/문제해결)", "상 (심화 학술이론)", "하 (기초 사실 확인)"], index=0)
    difficulty = diff_choice[0]
    
    st.markdown('<div class="privacy-notice-box"><div class="privacy-notice-title">🔒 개인정보 안심 처리</div><p class="privacy-notice-desc">인적사항, 고교명, 가족관계 등 대입 블라인드 항목은 자동 마스킹 처리되니 안심하셔도 됩니다.</p></div>', unsafe_allow_html=True)

if not GEMINI_API_KEY:
    st.error("⚠️ 서버 설정(Secrets)에 GEMINI_API_KEY가 등록되지 않았습니다.")
    st.stop()

# 7. 메인 입력 탭 ([방법 1] 텍스트 입력 우선)
tab1, tab2 = st.tabs(["✍️ [방법 1] 학생부 텍스트 직접 입력", "📂 [방법 2] 학생부 PDF 업로드"])
input_text = ""

with tab1:
    direct_text = st.text_area(
        "학생부 내용을 복사해 붙여넣으세요",
        height=220,
        placeholder="과세특, 창체, 행특 내용을 이곳에 붙여넣으세요..."
    )
    if direct_text:
        input_text = direct_text

with tab2:
    uploaded_pdf = st.file_uploader("학생부 PDF 파일을 올려주세요", type=["pdf"])
    if uploaded_pdf:
        with st.spinner("PDF 파일에서 텍스트를 정밀 추출하고 있습니다..."):
            input_text = extract_text_from_pdf(uploaded_
