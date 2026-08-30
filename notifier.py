import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_notification(job_meta, parsed_data):
  """새로 감지된 채용 공고와 AI 분석 요약을 텔레그램으로 전송합니다."""
  if not BOT_TOKEN or not CHAT_ID:
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

  message = f"""<b>[병역일터] 신규 공고 등록</b>

- 회사명: {company}
- 공고명: {title}
- 마감일: {deadline}
----------------------------------------
- 채용 유형: {recruit_str}
- 모집 직무: {positions_str}
- 기술 스택: <code>{stacks_str}</code>
----------------------------------------

<b>[AI 분석 요약]</b>
{summary}

- 원문 공고: <a href="{link}">병역일터 바로가기</a>"""

  if apply_url:
    message += f'\n- 채용 페이지: <a href="{apply_url}">공식 지원 링크</a>'

  payload = {
      "chat_id": CHAT_ID,
      "text": message,
      "parse_mode": "HTML",
      "disable_web_page_preview": True,
  }

  try:
    res = requests.post(url, json=payload, timeout=10)
    return res.status_code == 200
  except Exception as e:
    print(f"[ERROR] 텔레그램 전송 실패: {e}")
    return False


def send_pipeline_summary(total_new_jobs, total_skipped_jobs):
  """수집 작업 종료 시 최종 결과를 텔레그램으로 회신합니다."""
  if not BOT_TOKEN or not CHAT_ID:
    return False

  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

  if total_new_jobs == 0:
    message = (
        "[수집 완료] 새로 등록된 공고가 없습니다. (기존 공고"
        f" {total_skipped_jobs}건 확인)"
    )
  else:
    message = (
        f"[수집 완료] 총 {total_new_jobs}건의 신규 공고가 등록되었습니다."
        f" (기존 공고: {total_skipped_jobs}건)"
    )

  payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}

  try:
    res = requests.post(url, json=payload, timeout=10)
    return res.status_code == 200
  except Exception as e:
    print(f"[ERROR] 요약 알림 전송 실패: {e}")
    return False