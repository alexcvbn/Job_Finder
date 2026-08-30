import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_notification(job_meta, parsed_data):
  """새로 감지된 채용 공고와 AI 분석 요약을 텔레그램으로 전송합니다."""
  if not BOT_TOKEN or not CHAT_ID:
    print("텔레그램 설정이 .env에 없어 알림을 건너뜁니다.")
    return False

  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

  company = job_meta.get("company", "회사명 미상")
  title = job_meta.get("title", "공고 제목 없음")
  deadline = job_meta.get("deadline", "상시 채용")
  link = job_meta.get("link", "")

  tech_stacks = parsed_data.get("tech_stacks", [])
  stacks_str = ", ".join(tech_stacks) if tech_stacks else "정보 없음"

  recruit_types = parsed_data.get("recruit_types", [])
  recruit_str = ", ".join(recruit_types) if recruit_types else "정보 없음"

  positions = parsed_data.get("positions", [])
  positions_str = ", ".join(positions) if positions else "정보 없음"

  summary = parsed_data.get("summary", "AI 요약 없음")
  apply_url = parsed_data.get("apply_url")

  # HTML 태그를 사용한 깔끔한 카드형 메시지 서식 구성
  message = f"""<b>[병역일터] 새로운 IT 지정업체 공고</b>

<b>회사명</b>: {company}
<b>공고명</b>: {title}
<b>마감일</b>: {deadline}

━━━━━━━━━━━━━━━━━━━
<b>채용 유형</b>: {recruit_str}
<b>모집 직무</b>: {positions_str}
<b>기술 스택</b>: <code>{stacks_str}</code>
━━━━━━━━━━━━━━━━━━━

<b>AI 요약</b>
{summary}

<a href="{link}">병무청 원문 공고 보기</a>"""

  if apply_url:
    message += f'\n<a href="{apply_url}">공식 채용 페이지 바로가기</a>'

  payload = {
      "chat_id": CHAT_ID,
      "text": message,
      "parse_mode": "HTML",
      "disable_web_page_preview": True,
  }

  try:
    response = requests.post(url, json=payload, timeout=10)
    if response.status_code == 200:
      print("텔레그램 푸시 알림 전송 완료!")
      return True
    else:
      print(
          f"텔레그램 전송 실패 ({response.status_code}):"
          f" {response.text}"
      )
      return False
  except Exception as e:
    print(f"텔레그램 네트워크 에러: {e}")
    return False


if __name__ == "__main__":
  # 단독 알림 테스트
  test_meta = {
      "company": "테스트 기업",
      "title": "[전문연구요원/산업기능요원] 백엔드 엔지니어 채용",
      "deadline": "2026-12-31",
      "link": "https://work.mma.go.kr",
  }
  test_parsed = {
      "recruit_types": ["보충역 신규", "보충역 전직"],
      "positions": ["백엔드 개발자", "인프라 엔지니어"],
      "tech_stacks": ["C++", "Go", "Docker", "Linux"],
      "summary": (
          "대용량 분산 시스템 백엔드 개발자를 모집합니다.\n보충역 신규 편입 및"
          " 전직 지원이 모두 가능합니다."
      ),
      "apply_url": "https://example.com/careers",
  }

  print("텔레그램 알림 테스트 전송 중...")
  send_telegram_notification(test_meta, test_parsed)