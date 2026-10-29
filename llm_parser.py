import os
import json
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def parse_job_remark_with_ai(company_name: str, title: str, remark_text: str) -> dict:
    """
    병역일터 공고 제목과 상세 요강을 분석하여 구조화된 JSON으로 반환합니다.
    """
    fallback_result = {
        "positions": [],
        "tech_stacks": [],
        "summary": "상세 요강이 제공되지 않았거나 분석할 수 없는 형식입니다."
    }

    if not GEMINI_API_KEY:
        print("[ERROR] GEMINI_API_KEY가 설정되지 않았습니다.")
        return fallback_result

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"""
다음은 보충역 산업기능요원 채용 공고 정보입니다.
공고 제목과 본문 내용을 모두 검토하여 아래 JSON 스키마에 맞춰 정확히 JSON 데이터만 출력하세요.

[회사명]: {company_name}
[공고 제목]: {title}
[공고 내용]: {remark_text}

[출력 요구 JSON 포맷]:
{{
  "positions": ["공고 제목이나 본문에 명시된 모집 직무명을 추출하세요, 없으면 빈 배열을 반환하세요"],
  "tech_stacks": [공고 제목이나 본문에 언급된 핵심 기술 스택 리스트],
  "summary": "지원 자격, 담당 업무, 우대 사항을 핵심 위주로 요약한 2~3줄 한국어 설명"
}}
"""

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        raw_text = response.text.strip()
        clean_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.MULTILINE).strip()
        data = json.loads(clean_text)

        return {
            "positions": data.get("positions", []),
            "tech_stacks": data.get("tech_stacks", []),
            "summary": data.get("summary", "요약 없음")
        }

    except Exception as e:
        print(f"[ERROR] '{company_name}' LLM 파싱 중 예외 발생: {e}")
        return fallback_result