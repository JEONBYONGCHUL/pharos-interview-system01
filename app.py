import os
import re
import json
import urllib.request
import streamlit as st
import streamlit.components.v1 as components
from pypdf import PdfReader

# 1. 페이지 레이아웃 및 브라우저 탭 설정
st.set_page_config(
    page_title="2028 대입 학생부 기반 모의 면접",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 고급 브랜드 CSS 스타일링
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    /* 상단 프리미엄 헤더 박스 */
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
    
    /* 로고 & 블로그 안내 링크 영역 */
    .brand-meta-box {
        margin-top: 18px;
        padding-top: 16px;
        border-top: 1px solid rgba(148, 163, 184, 0.2);
        display: flex;
        align-items: center;
        gap: 16px;
    }
    
    .brand-logo-container {
        width: 120px;
        height: 52px;
        background: #ffffff;
        border-radius: 8px;
        padding: 4px 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    
    .brand-meta-text {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .brand-blog-name {
        font-size: 14.5px;
        font-weight: 700;
        color: #f1f5f9;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .brand-blog-url {
        font-size: 13.5px;
        color: #38bdf8;
        text-decoration: none;
        transition: color 0.2s;
    }
    .brand-blog-url:hover {
        color: #7dd3fc;
        text-decoration: underline;
    }

    /* 사이드바 프리미엄 스타일 */
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
    
    /* 하단 안심 안내 카드 */
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
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .privacy-notice-desc {
        font-size: 12px;
        color: #475569;
        line-height: 1.5;
        margin: 0;
    }

    /* 실행 버튼 고급 로열 블루 그라데이션 커스텀 */
    div.stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 24px !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
        box-shadow: 0 6px 18px rgba(2, 132, 199, 0.45) !important;
        transform: translateY(-1px) !important;
    }

    /* 면접 결과 카드 디자인 */
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
""", unsafe_allow_html=True)

# 3. 상단 헤더 및 파로스 등대 로고 (코드 깨짐 없는 완전 격리 렌더링)
st.markdown("""
<div class="brand-header-box">
    <div class="brand-title">2028 대입 학생부 기반 모의 면접</div>
    <div class="brand-subtitle">학생부 기반 맞춤형 면접 질문 추출 및 실전 구술 음성 지원 시스템</div>
    <div class="brand-meta-box">
        <div class="brand-logo-container">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
                <defs>
                    <linearGradient id="beam" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#9333ea" stop-opacity="0.9"/>
                        <stop offset="100%" stop-color="#475569" stop-opacity="0.7"/>
                    </linearGradient>
                    <linearGradient id="bodyGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#831843"/>
                        <stop offset="50%" stop-color="#9d174d"/>
                        <stop offset="100%" stop-color="#be185d"/>
                    </linearGradient>
                </defs>
                <polygon points="120,45 180,68 180,78 120,68" fill="url(#beam)"/>
                <polygon points="120,85 180,92 180,102 120,95" fill="#64748b"/>
                <polygon points="280,45 220,68 220,78 280,68" fill="#64748b"/>
                <polygon points="280,85 220,92 220,102 280,95" fill="url(#beam)"/>
                <polygon points="200,28 196,48 204,48" fill="#831843"/>
                <path d="M182,65 Q200,48 218,65 Z" fill="#831843"/>
                <rect x="180" y="65" width="40" height="28" fill="#ffffff" stroke="#831843" stroke-width="4"/>
                <line x1="193" y1="65" x2="193" y2="93" stroke="#831843" stroke-width="3"/>
                <line x1="207" y1="65" x2="207" y2="93" stroke="#831843" stroke-width="3"/>
                <polygon points="175,98 225,98 245,200 155,200" fill="url(#bodyGrad)"/>
                <polygon points="171,120 229,120 236,152 164,152" fill="#be185d"/>
                <polygon points="160,172 240,172 243,186 157,186" fill="#be185d"/>
                <polygon points="177,98 190,98 215,200 202,200" fill="#fbcfe8" opacity="0.4"/>
                <rect x="145" y="200" width="110" height="8" rx="3" fill="#831843"/>
                <text x="200" y="260" font-family="'Pretendard', sans-serif" font-size="44" font-weight="900" fill="#475569" text-anchor="middle" letter-spacing="4">파로스 대입 랩</text>
            </svg>
        </div>
        <div class="brand-meta-text">
            <span class="brand-blog-name">🏛️ 파로스대입랩 네이버블로그</span>
            <a class="brand-blog-url" href="http://blog.naver.com/pharoslab" target="_blank">http://blog.naver.com/pharoslab</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. 서버 API 키 로드
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def sanitize_student_record(text: str, custom_name: str = "") -> str:
    sanitized = text
    if custom_name and len(custom_name.strip()) >= 2:
        sanitized = re.sub(re.escape(custom_name.strip()), "[OO학생]", sanitized)
    sanitized = re.sub(r'[가-힣]{2,10}(고등학교|여고|남고|외고|과고|예고|체고|마이스터고|공고|상고|고)', "[OO고등학교]", sanitized)
    sanitized = re.sub(r'\b\d{6}[-\s]?[1-4]\d{6}\b', '[주민번호 마스킹]', sanitized)
    sanitized = re.sub(r'\b(19\d{2}|20\d{2})[.-년\s]+(0?[1-9]|1[0-2])[.-월\s]+(0?[1-9]|[12]\d|3[01])일?\b', '[생년월일 마스킹]', sanitized)
    sanitized = re.sub(r'01[016789][-\s]?\d{3,4}[-\s]?\d{4}', '[연락처 마스킹]', sanitized)
    sanitized = re.sub(r'\b(아버지|어머니|부모님|부친|모친|형|누나|오빠|언니|동생|외조부|조부|외조모|조모|삼촌|이모|고모)\b', "[가족관계]", sanitized)
    return sanitized

def build_system_instruction(question_count: int, difficulty: str) -> str:
    diff_map = {
        "하": "기초 사실 확인형: 활동의 진위 여부와 본인 역할 중심",
        "중": "탐구 과정 및 문제해결형: 인과관계, 오차 극복 논리, 전공 기초 연계 중심",
        "상": "심화 이론 및 메커니즘형: 학술 이론 배경, 원리적 작동 구조, 비판적 반론 중심"
    }
    diff_text = diff_map.get(difficulty, "")

    return f"""
당신은 대한민국 명문 대학 대입 학생부종합전형 수석 입학사정관입니다.
제공된 학생부 텍스트를 분석하여 [{difficulty} 난이도: {diff_text}]에 부합하는 면접 질문 총 {question_count}문항을 생성하세요.

반드시 마크다운 백틱 없이 순수 JSON 포맷으로만 응답하세요:
{{
  "major": "지원 전공",
  "difficulty": "{difficulty}",
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
}}
"""

def call_gemini_api(prompt: str, count: int, diff: str) -> dict:
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
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
def render_tts_button(text: str, button_id: str):
    clean_text = json.dumps(text, ensure_ascii=False)
    template = """
    <div style="margin-bottom: 16px;">
        <button id="btn_ID" style="
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: linear-gradient(180deg, #0284c7 0%, #0369a1 100%);
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 7px 15px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(2, 132, 199, 0.25);
        ">
            🔊 음성으로 질문 듣기
        </button>
        <span id="status_ID" style="font-size: 12px; color: #64748b; margin-left: 10px;"></span>
    </div>
    <script>
        const btn_ID = document.getElementById('btn_ID');
        const status_ID = document.getElementById('status_ID');
        const textToRead = TEXT_PLACEHOLDER;
        
        btn_ID.addEventListener('click', function() {
            if (!('speechSynthesis' in window)) {
                alert('사용 중이신 브라우저가 음성 듣기를 지원하지 않습니다.');
                return;
            }
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(textToRead);
            utter.lang = 'ko-KR';
            utter.rate = 0.93;
            
            const voices = window.speechSynthesis.getVoices();
            const koVoice = voices.find(v => v.lang && (v.lang.includes('ko') || v.lang.includes('KO')));
            if (koVoice) {
                utter.voice = koVoice;
            }
            
            utter.onstart = function() {
                btn_ID.style.background = '#475569';
                status_ID.innerText = '낭독 중...';
            };
            utter.onend = function() {
                btn_ID.style.background = 'linear-gradient(180deg, #0284c7 0%, #0369a1 100%)';
                status_ID.innerText = '';
            };
            utter.onerror = function() {
                btn_ID.style.background = 'linear-gradient(180deg, #0284c7 0%, #0369a1 100%)';
                status_ID.innerText = '';
            };
            window.speechSynthesis.speak(utter);
        });
        
        if ('speechSynthesis' in window && window.speechSynthesis.onvoiceschanged !== undefined) {
            window.speechSynthesis.onvoiceschanged = () => { window.speechSynthesis.getVoices(); };
        }
    </script>
    """
    html_code = template.replace("btn_ID", f"btn_{button_id}").replace("status_ID", f"status_{button_id}").replace("TEXT_PLACEHOLDER", clean_text)
    components.html(html_code, height=48)

# 6. 사이드바 - 고급 모의 면접 조건 설정
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header-box">
        <div class="sidebar-header-title">⚙️ 모의 면접 조건 설정</div>
    </div>
    """, unsafe_allow_html=True)
    
    student_name = st.text_input("학생 실명 (마스킹용)", placeholder="홍길동 (미입력 가능)")
    target_major = st.text_input("지원 희망 전공/학과", placeholder="예: 신소재공학과, 의예과")
    
    q_count = st.selectbox(
        "추출 면접 문항 수", 
        [10, 5, 3], 
        index=0, 
        format_func=lambda x: f"🎯 {x}문항 심층 면접"
    )
    
    diff_labels = {
        "하": "난이도 [하]: 기초 사실 확인",
        "중": "난이도 [중]: 탐구/문제해결",
        "상": "난이도 [상]: 심화 학술이론"
    }
    difficulty = st.selectbox(
        "평가 난이도", 
        ["하", "중", "상"], 
        index=1,
        format_func=lambda x: diff_labels.get(x, x)
    )
    
    # 하단 개인정보 안심 처리 안내 문구
    st.markdown("""
    <div class="privacy-notice-box">
        <div class="privacy-notice-title">🔒 개인정보 안심 처리</div>
        <p class="privacy-notice-desc">
            인적사항, 고교명, 가족관계 등 대입 블라인드 항목은 자동 마스킹 처리되니 안심하셔도 됩니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

if not GEMINI_API_KEY:
    st.error("⚠️ 서버 설정(Secrets)에 GEMINI_API_KEY가 등록되지 않았습니다.")
    st.stop()

# 7. 메인 입력 탭
tab1, tab2 = st.tabs(["📂 [방법 1] 학생부 PDF 업로드", "✍️ [방법 2] 학생부 텍스트 직접 입력"])
input_text = ""

with tab1:
    uploaded_pdf = st.file_uploader("학생부 PDF 파일을 올려주세요", type=["pdf"])
    if uploaded_pdf:
        with st.spinner("PDF 파일에서 텍스트를 정밀 추출하고 있습니다..."):
            input_text = extract_text_from_pdf(uploaded_pdf)
            st.success("✅ 학생부 PDF 텍스트 추출 완료")

with tab2:
    direct_text = st.text_area(
        "학생부 내용을 복사해 붙여넣으세요",
        height=220,
        placeholder="과세특, 창체, 행특 내용을 이곳에 붙여넣으세요..."
    )
    if not input_text:
        input_text = direct_text

# 8. 질문 추출 버튼 및 렌더링
if st.button("🚀 면접 질문 추출하기", use_container_width=True):
    if not input_text.strip():
        st.warning("⚠️ 학생부 내용을 입력하거나 PDF를 올려주세요.")
    else:
        with st.spinner("사정관 AI가 학생부 탐구 인과관계 및 교과 개념을 정밀 분석 중입니다..."):
            sanitized = sanitize_student_record(input_text, student_name)
            user_prompt = f"지원 전공: {target_major or '미지정'}\n\n[학생부 원문]\n{sanitized}"
            try:
                result = call_gemini_api(user_prompt, q_count, difficulty)
                st.success(f"🎉 총 {q_count}문항 추출 완료 (난이도: {difficulty})")
                st.markdown("---")

                q_num = 1
                for sec in result.get("sections", []):
                    st.markdown(f"#### 📁 {sec.get('category')}")
                    for item in sec.get("questions", []):
                        q_text = item.get('question', '')
                        source_quote = item.get('source_quote', '')
                        intent = item.get('intent', '')
                        high_score = item.get('high_score_guide', '')
                        q_type = item.get('type', '심층 면접')

                        st.markdown(f"""
                        <div class="interview-card">
                            <span class="badge-type">[{q_type}] · 난이도 {difficulty}</span>
                            <div class="question-title">Q{q_num}. {q_text}</div>
                            <div class="meta-row">📌 <b>학생부 근거:</b> <i>"{source_quote}"</i></div>
                            <div class="meta-row">🎯 <b>출제 의도:</b> {intent}</div>
                            <div class="meta-highlight">💡 <b>고득점 답변 가이드:</b> {high_score}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        render_tts_button(q_text, f"q_{q_num}")
                        q_num += 1
                        
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
