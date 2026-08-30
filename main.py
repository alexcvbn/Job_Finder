import time
from crawler import fetch_job_detail, fetch_mma_jobs
from database import extract_job_no, init_db, is_job_exists, save_job
from llm_parser import parse_job_remark_with_ai
from notifier import send_pipeline_summary, send_telegram_notification

def run_pipeline():
  """병역일터 수집 -> 중복 검사 -> json 구조화 -> DB 적재 전체 파이프라인을 실행합니다."""
  # 1. DB 테이블 초기화 (테이블이 없으면 생성)
  init_db()

  page = 1
  total_new_jobs = 0
  total_skipped_jobs = 0

  print("공고 자동 수집 및 AI 분석 파이프라인 시작\n")

  while True: #공고가 끝날때까지 파이프라인 진행

    print(f"\n[{page} 페이지] 공고 목록 조회 중...")
    jobs = fetch_mma_jobs(page_index=page)

    # 더 이상 가져올 공고가 없으면(마지막 페이지를 넘어가면) 자동 종료!
    if not jobs:
      print("   -> 마지막 페이지에 도달했습니다. 수집을 종료합니다.")
      break

    for job in jobs:
      job_no = extract_job_no(job["link"])
      if is_job_exists(job_no):
        print(f"[건너뜀] {job['company']}")
        total_skipped_jobs += 1
        continue

      print(f"[새 공고] {job['company']} AI 분석 중...")
      detail = fetch_job_detail(job["link"])
      raw_remark = detail.get("remark") or str(detail.get("detail_info", ""))

      parsed_data = parse_job_remark_with_ai(job["company"], raw_remark)
      save_job(job, parsed_data)
      send_telegram_notification(job, parsed_data)
      total_new_jobs += 1
      time.sleep(1)
 
    page += 1  #다음 페이지로 이동
    time.sleep(1)

    send_pipeline_summary(total_new_jobs, total_skipped_jobs)

if __name__ == "__main__":
  # 테스트로 1페이지만 먼저 전체 파이프라인 실행
  run_pipeline()