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

# 2. 고품격 브랜드 스타일링 (CSS)
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    /* 헤더 컨테이너 */
    .brand-header-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 36px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* 타이틀 (화면 크기에 따른 줄바꿈 방지) */
    .brand-title {
        font-size: clamp(22px, 3.2vw, 36px);
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #f8fafc;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin: 0;
        line-height: 1.2;
    }
    
    /* 서브타이틀 */
    .brand-subtitle {
        font-size: clamp(13px, 1.4vw, 16px);
        color: #94a3b8;
        font-weight: 400;
        margin-top: 10px;
        margin-bottom: 0px;
        letter-spacing: -0.01em;
    }
    
    /* 브랜드 링크 영역 */
    .brand-meta-box {
        margin-top: 20px;
        padding-top: 16px;
        border-top: 1px solid rgba(148, 163, 184, 0.2);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .brand-logo-badge {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white;
        font-size: 13px;
        font-weight: 800;
        padding: 5px 11px;
        border-radius: 6px;
        letter-spacing: 0.04em;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    
    .brand-blog-name {
        font-size: 14px;
        font-weight: 700;
        color: #e2e8f0;
    }
    
    .brand-blog-url {
        font-size: 13px;
        color: #38bdf8;
        text-decoration: none;
        transition: color 0.2s;
    }
    .brand-blog-url:hover {
        color: #7dd3fc;
        text-decoration: underline;
    }
    
    /* 사이드바 프리미엄 카드 */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* 질문 출력 카드 */
    .interview-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #0284c7;
        border-radius: 12px;
        padding: 22px 24px;
        margin-bottom: 22px;
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
        margin-bottom: 14px;
    }
    
    .meta-row {
        font-size: 13.5px;
        color: #475569;
        margin-bottom: 7px;
        line-height: 1.5;
    }
    
    .meta-highlight {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
        padding: 9px 13px;
        border-radius: 8px;
        font-size: 13.5px;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# 3. 브랜드 헤더 렌더링
st.markdown("""
<div class="brand-header-box">
    <div class="brand-title">2028 대입 학생부 기반 모의 면접</div>
    <div class="brand-subtitle">학생부 기반 맞춤형 면접 질문 추출 및 실전 구술 음성 지원 시스템</div>
    <div class="brand-meta-box">
        <div class="brand-logo-badge">🏛️ PHAROS</div>
        <div>
            <span class="brand-blog-name">파로스대입랩 네이버블로그</span>&nbsp;&nbsp;
            <a class="brand-blog-url" href="http://blog.naver.com/pharoslab" target="_blank">http://blog.naver.com/pharoslab</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. 서버 키 검증
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))[cite: 15]

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)[cite: 15]
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])[cite: 15]

def sanitize_student_record(text: str, custom_name: str = "") -> str:
    sanitized = text[cite: 15]
    if custom_name and len(custom_name.strip()) >= 2:[cite: 15]
        sanitized = re.sub(re.escape(custom_name.strip()), "[OO학생]", sanitized)[cite: 15]
    sanitized = re.sub(r'[가-힣]{2,10}(고등학교|여고|남고|외고|과고|예고|체고|마이스터고|공고|상고|고)', "[OO고등학교]", sanitized)[cite: 15]
    sanitized = re.sub(r'\b\d{6}[-\s]?[1-4]\d{6}\b', '[주민번호 마스킹]', sanitized)[cite: 15]
    sanitized = re.sub(r'\b(19\d{2}|20\d{2})[.-년\s]+(0?[1-9]|1[0-2])[.-월\s]+(0?[1-9]|[12]\d|3[01])일?\b', '[생년월일 마스킹]', sanitized)[cite: 15]
    sanitized = re.sub(r'01[016789][-\s]?\d{3,4}[-\s]?\d{4}', '[연락처 마스킹]', sanitized)[cite: 15]
    sanitized = re.sub(r'\b(아버지|어머니|부모님|부친|모친|형|누나|오빠|언니|동생|외조부|조부|외조모|조모|삼촌|이모|고모)\b', "[가족관계]", sanitized)[cite: 15]
    return sanitized[cite: 15]

def build_system_instruction(question_count: int, difficulty: str) -> str:
    diff_text = {
        "하": "기초 사실 확인형: 활동의 진위 여부와 본인 역할 중심",
        "중": "탐구 과정 및 문제해결형: 인과관계, 오차 극복 논리, 전공 기초 연계 중심",
        "상": "심화 이론 및 메커니즘형: 학술 이론 배경, 원리적 작동 구조, 비판적 반론 중심"
    }.get(difficulty, "")[cite: 15]

    return f"""
당신은 대한민국 명문 대학 대입 학생부종합전형 수석 입학사정관입니다.
제공된 학생부 텍스트를 분석하여 [{difficulty} 난이도: {diff_text}]에 부합하는 면접 질문 총 {question_count}문항을 생성하세요.

반드시 마크다운 백틱 없이 순수 JSON 포맷으로만 응답하세요:
{{
  "major": "지원 전공",
  "difficulty": "{difficulty}",
  "sections": [
    {{
      "category": "영역 구분명 (예: 자율·진로활동, 국어·사회 교과 과세특 등)",
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
"""[cite: 15]

def call_gemini_api(prompt: str, count: int, diff: str) -> dict:
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}[cite: 15]
    sys_inst = build_system_instruction(count, diff)[cite: 15]
    body = {
        "contents": [{"role": "user", "parts": [{"text": f"{sys_inst}\n\n{prompt}"}]}],[cite: 15]
        "generationConfig": {"temperature": 0.7, "responseMimeType": "application/json"}[cite: 15]
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')[cite: 15]
    with urllib.request.urlopen(req) as resp:[cite: 15]
        data = json.loads(resp.read().decode('utf-8'))[cite: 15]
        t = data['candidates'][0]['content']['parts'][0]['text'].strip()[cite: 15]
        if t.startswith("```json"): t = t[7:][cite: 15]
        if t.startswith("```"): t = t[3:][cite: 15]
        if t.endswith("```"): t = t[:-3][cite: 15]
        return json.loads(t.strip())[cite: 15]

# 5. 견고한 음성 합성 컴포넌트 (Web Speech API 최적화)
def render_tts_button(text: str, button_id: str):
    clean_text = text.replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
    html_code = f"""
    <div style="margin-top: 10px;">
        <button id="btn_{button_id}" style="
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: linear-gradient(180deg, #0284c7 0%, #0369a1 100%);
            color: #ffffff;
            border: none;
            border-radius: 7px;
            padding: 8px 16px;
            font-size: 13.5px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(2, 132, 199, 0.25);
            transition: all 0.2s ease;
        ">
            🔊 음성으로 질문 듣기
        </button>
        <span id="status_{button_id}" style="font-size: 12px; color: #64748b; margin-left: 10px;"></span>
    </div>
    <script>
        const btn_{button_id} = document.getElementById('btn_{button_id}');
        const status_{button_id} = document.getElementById('status_{button_id}');
        
        btn_{button_id}.addEventListener('click', function() {{
            if (!('speechSynthesis' in window)) {{
                alert('사용 중이신 브라우저가 음성 듣기를 지원하지 않습니다. Chrome 또는 Edge 브라우저를 권장합니다.');
                return;
            }}
            
            window.speechSynthesis.cancel();
            
            const utter = new SpeechSynthesisUtterance("{clean_text}");
            utter.lang = 'ko-KR';
            utter.rate = 0.95;
            utter.pitch = 1.0;
            
            let voices = window.speechSynthesis.getVoices();
            let koVoice = voices.find(v => v.lang.includes('ko') || v.lang.includes('KO'));
            if (koVoice) {{
                utter.voice = koVoice;
            }}
            
            utter.onstart = function() {{
                btn_{button_id}.style.background = '#475569';
                status_{button_id}.innerText = '낭독 중...';
            }};
            
            utter.onend = function() {{
                btn_{button_id}.style.background = 'linear-gradient(180deg, #0284c7 0%, #0369a1 100%)';
                status_{button_id}.innerText = '';
            }};
            
            utter.onerror = function() {{
                btn_{button_id}.style.background = 'linear-gradient(180deg, #0284c7 0%, #0369a1 100%)';
                status_{button_id}.innerText = '';
            }};
            
            window.speechSynthesis.speak(utter);
        }});
        
        if ('speechSynthesis' in window && window.speechSynthesis.onvoiceschanged !== undefined) {{
            window.speechSynthesis.onvoiceschanged = () => {{ window.speechSynthesis.getVoices(); }};
        }}
    </script>
    """
    components.html(html_code, height=52)

# 6. 사이드바 - 고급 설정 패널
with st.sidebar:
    st.markdown("### ⚙️ 모의면접 조건 설정")
    st.markdown("---")
    student_name = st.text_input("학생 실명 (마스킹용)", placeholder="홍길동 (미입력 가능)")[cite: 15]
    target_major = st.text_input("지원 희망 전공/학과", placeholder="예: 경영학과, 기계공학과")[cite: 15]
    
    q_count = st.selectbox(
        "추출 면접 문항 수", 
        [10, 5, 3], 
        index=0, 
        format_func=lambda x: f"🎯 {x}문항 심층 면접"
    )[cite: 15]
    
    difficulty = st.selectbox(
        "평가 난이도", 
        ["하", "중", "상"], 
        index=1,
        format_func=lambda x: f"난이도 [{x}]: " + {"하": "기초 사실 확인", "중": "탐구/문제해결", "상": "심화 학술이론"}[x]
    )[cite: 15]
    
    st.markdown("---")
    st.caption("🔒 **개인정보 완벽 안심 처리**")
    st.caption("인적사항, 출신 고교명, 가족관계 등 대입 블라인드 필수 항목은 자동으로 암호화 마스킹 처리된 후 사정관 AI로 전달됩니다.")

if not GEMINI_API_KEY:
    st.error("⚠️ 서버 설정(Secrets)에 GEMINI_API_KEY가 등록되지 않았습니다.")[cite: 15]
    st.stop()[cite: 15]

# 7. 메인 입력 탭
tab1, tab2 = st.tabs(["📂 [방법 1] 학생부 PDF 업로드", "✍️ [방법 2] 학생부 텍스트 직접 입력"])[cite: 15]
input_text = ""[cite: 15]

with tab1:
    uploaded_pdf = st.file_uploader("학생부 PDF 파일을 마우스로 끌어다 놓으세요", type=["pdf"])[cite: 15]
    if uploaded_pdf:[cite: 15]
        with st.spinner("PDF 파일에서 텍스트를 추출하고 있습니다..."):
            input_text = extract_text_from_pdf(uploaded_pdf)[cite: 15]
            st.success("✅ 학생부 PDF 텍스트 추출이 완료되었습니다.")

with tab2:
    direct_text = st.text_area(
        "과세특, 자율·진로활동, 행특 내용을 복사해서 붙여넣으세요",
        height=230,
        placeholder="생기부 텍스트를 이곳에 붙여넣으세요..."
    )[cite: 15]
    if not input_text:[cite: 15]
        input_text = direct_text[cite: 15]

# 8. 질문 추출 실행 버튼
if st.button("🚀 심층 면접 질문 추출하기", type="primary", use_container_width=True):[cite: 15]
    if not input_text.strip():[cite: 15]
        st.warning("⚠️ 학생부 텍스트를 입력하거나 PDF 파일을 업로드해 주세요.")
    else:
        with st.spinner("사정관 AI가 학생부 탐구 인과관계 및 핵심 개념을 다각도로 분석 중입니다..."):
            sanitized = sanitize_student_record(input_text, student_name)[cite: 15]
            user_prompt = f"지원 전공: {target_major or '미지정'}\n\n[학생부 원문]\n{sanitized}"[cite: 15]
            try:
                result = call_gemini_api(user_prompt, q_count, difficulty)[cite: 15]
                st.success(f"🎉 총 {q_count}문항의 사정관 면접 질문 추출이 완료되었습니다! (평가 난이도: {difficulty})")[cite: 15]
                st.markdown("---")

                q_num = 1[cite: 15]
                for sec in result.get("sections", []):[cite: 15]
                    st.markdown(f"#### 📁 {sec.get('category')}")
                    for item in sec.get("questions", []):[cite: 15]
                        q_text = item.get('question', '')[cite: 15]
                        source_quote = item.get('source_quote', '')[cite: 15]
                        intent = item.get('intent', '')[cite: 15]
                        high_score = item.get('high_score_guide', '')[cite: 15]
                        q_type = item.get('type', '심층 면접')[cite: 15]

                        st.markdown(f"""
                        <div class="interview-card">
                            <span class="badge-type">[{q_type}] · 난이도 {difficulty}</span>
                            <div class="question-title">Q{q_num}. {q_text}</div>
                            <div class="meta-row">📌 <b>학생부 근거:</b> <i>"{source_quote}"</i></div>
                            <div class="meta-row">🎯 <b>출제 의도:</b> {intent}</div>
                            <div class="meta-highlight">💡 <b>고득점 답변 가이드:</b> {high_score}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        # 전용 음성 재생 모듈 임베딩
                        render_tts_button(q_text, f"q_{q_num}")
                        q_num += 1[cite: 15]
                        
            except Exception as e:
                st.error(f"면접 질문 생성 중 오류가 발생했습니다: {str(e)}")[cite: 15]
