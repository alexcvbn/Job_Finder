import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def parse_job_remark_with_ai(company_name, raw_text):
  """비정형 공고 비고를 Gemini를 이용해 정형 JSON 데이터로 추출합니다."""
  if not raw_text.strip():
    return {}

  prompt = f"""
    당신은 IT 채용 공고 전문 데이터 분석가입니다.
    아래는 '{company_name}'의 병무청 채용공고 본문(비고란) 텍스트입니다.
    이 텍스트를 정밀 분석하여 기술 스택과 채용 조건을 JSON으로 추출하세요.

    [공고 원문]
    {raw_text}

    [추출 규칙]
    1. recruit_types: 채용 유형 (예: ["보충역 신규", "보충역 전직", "현역 전직"] 등)
    2. positions: 모집하는 직무 목록 (예: ["백엔드", "프론트엔드", "iOS", "ML"] 등)
    3. tech_stacks: 요구하거나 우대하는 기술 스택 키워드 (예: ["Python", "Go", "C++", "Spring"] 등, 없으면 빈 배열)
    4. apply_url: 외부 지원 링크 URL (본문에 URL이 있으면 추출, 없으면 null)
    5. summary: 2줄 이내의 핵심 요약
    """

  try:
    # response_mime_type을 지정하여 순수 JSON만 반환하도록 강제
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,  # 환각 방지를 위해 가장 보수적인 온도 설정
        ),
    )

    # 문자열 응답을 파이썬 딕셔너리로 변환
    structured_data = json.loads(response.text)
    return structured_data

  except Exception as e:
    print(f"ERROR: LLM 파싱 에러: {e}")
    return {}


'''
if __name__ == "__main__":
  # 앞서 크롤러가 수집했던 당근마켓 비고란 실제 텍스트 예시
  sample_danggeun_remark = """
    1. 채용 유형
    - 보충역 신규 편입
    - 보충역 전직 (현 업체 복무 6개월 이상 등 병무청 전직 요건 충족자)

    2. 모집 포지션
    - 아래 링크의 포지션 전체 (백엔드, 프론트엔드, iOS, Android, ML 등 / 세부 자격 요건은 각 공고 참고)
    - 기술 스택: Go, Python, TypeScript, Kafka, AWS

    3. 지원 링크: https://about.daangn.com/jobs/
    """

  print("당근마켓 공고 AI 분석 중...")
  result = parse_job_remark_with_ai("당근마켓", sample_danggeun_remark)

  print("\n=== ✨ LLM 구조화 추출 결과 ===")
  print(json.dumps(result, indent=2, ensure_ascii=False))

'''
