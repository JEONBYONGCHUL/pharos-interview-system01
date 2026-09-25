import os
import re
import json
import streamlit as st
from pypdf import PdfReader
import urllib.request

st.set_page_config(page_title="파로스 심층 모의면접관", page_icon="🎓", layout="wide")

# 서버 비밀 금고(Secrets)에서 키를 자동으로 읽어옵니다 (사용자 입력 불필요)
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
    diff_text = {
        "하": "기초 사실 확인형: 활동의 진위 여부와 본인 역할 중심",
        "중": "탐구 과정 및 문제해결형: 인과관계, 오차 극복 논리, 전공 기초 연계 중심",
        "상": "심화 이론 및 메커니즘형: 학술 이론 배경, 원리적 작동 구조, 비판적 반론 중심"
    }.get(difficulty, "")

    return f"""
당신은 대한민국 명문 대학 대입 학생부종합전형 수석 입학사정관입니다.
제공된 학생부 텍스트를 분석하여 [{difficulty} 난이도: {diff_text}]에 부합하는 면접 질문 총 {question_count}문항을 생성하세요.

반드시 마크다운 백틱 없이 순수 JSON 포맷으로만 응답하세요:
{{
  "major": "지원 전공",
  "difficulty": "{difficulty}",
  "sections": [
    {{
      "category": "영역 구분명",
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
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
    sys_inst = build_system_instruction(count, diff)
    body = {
        "contents": [{"role": "user", "parts": [{"text": f"{sys_inst}\n\n{prompt}"}]}],
        "generationConfig": {"temperature": 0.8, "responseMimeType": "application/json"}
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        t = data['candidates'][0]['content']['parts'][0]['text'].strip()
        if t.startswith("```json"): t = t[7:]
        if t.startswith("```"): t = t[3:]
        if t.endswith("```"): t = t[:-3]
        return json.loads(t.strip())

# UI 시작
st.title("🎓 파로스 대입 심층 모의면접관")
st.caption("학생부 기반 맞춤형 심층 면접 질문 추출 및 실전 구술 음성 지원 시스템")

if not GEMINI_API_KEY:
    st.error("⚠️ 서버 설정(Secrets)에 GEMINI_API_KEY가 등록되지 않았습니다.")
    st.stop()

with st.sidebar:
    st.header("⚙️ 모의면접 조건 설정")
    student_name = st.text_input("학생 실명 (마스킹용)", placeholder="홍길동")
    target_major = st.text_input("지원 전공/학과", placeholder="전자공학과 / 컴퓨터공학과")
    q_count = st.selectbox("추출 문항 수", [10, 5, 3], index=0, format_func=lambda x: f"{x}문항 모의면접")
    difficulty = st.selectbox("질문 난이도", ["하", "중", "상"], index=1)

tab1, tab2 = st.tabs(["📂 [방법 1] 학생부 PDF 업로드", "✍️ [방법 2] 학생부 텍스트 직접 입력"])
input_text = ""
with tab1:
    uploaded_pdf = st.file_uploader("학생부 PDF 파일 선택", type=["pdf"])
    if uploaded_pdf:
        input_text = extract_text_from_pdf(uploaded_pdf)
        st.success("✅ PDF 텍스트 추출 완료")

with tab2:
    direct_text = st.text_area("과세특, 창체, 행특 내용 붙여넣기", height=250)
    if not input_text:
        input_text = direct_text

if st.button("🚀 심층 면접 질문 추출하기", type="primary", use_container_width=True):
    if not input_text.strip():
        st.warning("학생부 내용을 입력하거나 PDF를 올려주세요.")
    else:
        with st.spinner("사정관 AI가 학생부를 정밀 분석하여 질문을 생성 중입니다..."):
            sanitized = sanitize_student_record(input_text, student_name)
            user_prompt = f"지원 전공: {target_major or '미지정'}\n\n[학생부 원문]\n{sanitized}"
            try:
                result = call_gemini_api(user_prompt, q_count, difficulty)
                st.success(f"총 {q_count}문항 추출이 완료되었습니다! (난이도: {difficulty})")

                q_num = 1
                for sec in result.get("sections", []):
                    st.markdown(f"### 📂 {sec.get('category')}")
                    for item in sec.get("questions", []):
                        q_text = item.get('question', '')
                        safe_q = q_text.replace("'", "\\'").replace('"', '&quot;').replace('\n', ' ')

                        st.markdown(f"""
                        <div style="background-color: #f8fafc; border-left: 4px solid #0284c7; padding: 14px 18px; margin-bottom: 10px; border-radius: 6px;">
                            <div style="font-size: 13px; color: #64748b; font-weight: bold;">[{item.get('type')}] (난이도: {difficulty})</div>
                            <h4 style="margin: 6px 0; color: #0f172a;">Q{q_num}. {q_text}</h4>
                            <div style="font-size: 13px; color: #475569; margin-bottom: 4px;">📌 <b>근거 문맥:</b> <i>{item.get('source_quote')}</i></div>
                            <div style="font-size: 13px; color: #334155; margin-bottom: 4px;">🎯 <b>출제 의도:</b> {item.get('intent')}</div>
                            <div style="font-size: 13px; color: #0369a1; font-weight: bold; margin-bottom: 8px;">💡 <b>고득점 답변 가이드:</b> {item.get('high_score_guide')}</div>
                            <button onclick="window.speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance('{safe_q}'); u.lang='ko-KR'; u.rate=0.92; window.speechSynthesis.speak(u);" 
                                    style="background-color: #0284c7; color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: bold;">
                                🔊 음성으로 질문 듣기
                            </button>
                        </div>
                        """, unsafe_allow_html=True)
                        q_num += 1
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")