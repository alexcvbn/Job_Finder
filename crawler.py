import json
import time
from bs4 import BeautifulSoup
from llm_parser import (  # 👈 [추가 1] 방금 만든 AI 파서 함수 가져오기
    parse_job_remark_with_ai,
)
import requests

URL = "https://work.mma.go.kr/caisBYIS/search/cygonggogeomsaek.do"
BASE_URL = "https://work.mma.go.kr"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
        " (KHTML, like Gecko) Version/26.3.1 Safari/605.1.15"
    ),
    "Referer": URL,
    "Content-Type": "application/x-www-form-urlencoded",
}


def fetch_mma_jobs(page_index=1):
  """목록 페이지에서 공고 메타데이터(제목, 회사명, 마감일, 상세링크) 목록을 가져옵니다."""
  payload = {
      "pageIndex": str(page_index),
      "pageUnit": "10",
      "eopjong_gbcd": "1",
      "ar_eopjong_gbcd": "11111,11112",
      "eopjong_gbcd_list": "11111,11112",
      "sido_addr": "서울특별시",
      "yeokjong_brcd": "002",
      "ar_bokrihs_cd": "",
      "bokrihs_cd_list": "",
      "gegyumo_cd": "",
      "eopche_nm": "",
      "sigungu_addr": "",
      "cyjemok_nm": "",
      "gyjogeon_cd": "",
  }

  try:
    response = requests.post(URL, headers=HEADERS, data=payload, timeout=10)
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="brd_list_n")
    if not table:
      return []

    tbody = table.find("tbody")
    if not tbody:
      return []

    rows = tbody.find_all("tr")
    job_list = []

    for row in rows:
      cols = row.find_all("td")
      if len(cols) < 5:
        continue

      title_tag = cols[0].find("a")
      title = title_tag.get_text(strip=True) if title_tag else ""
      relative_link = title_tag["href"] if title_tag else ""
      full_link = BASE_URL + relative_link if relative_link else ""

      company = cols[1].get_text(strip=True)
      deadline = cols[2].get_text(strip=True)
      created_at = cols[3].get_text(strip=True)

      job_list.append({
          "company": company,
          "title": title,
          "deadline": deadline,
          "created_at": created_at,
          "link": full_link,
      })

    return job_list

  except Exception as e:
    print(f"  [목록 수집 에러] {page_index}페이지 -> {e}")
    return []


def fetch_job_detail(detail_url):
    """
    상세 페이지에서 [비고 사항] 테이블 내부의 전체 텍스트(직무, 기술스택, 지원링크 등)를
    누락 없이 정확하게 추출합니다.
    """
    if not detail_url:
        return {"remark": "", "detail_info": {}, "raw_content": ""}

    try:
        response = requests.get(detail_url, headers=HEADERS, timeout=10)
        response.encoding = response.apparent_encoding or "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")

        remark_text = ""

        # 1. <caption> 태그 내 '비고' 텍스트로 테이블 탐색 (공백 영향 전혀 없음)
        for cap in soup.find_all("caption"):
            if "비고" in cap.get_text():
                target_table = cap.find_parent("table")
                if target_table:
                    remark_text = target_table.get_text(separator="\n", strip=True)
                    break

        # 2. summary 속성에 '비고'가 포함된 테이블 탐색 (와일드카드 부분 일치)
        if not remark_text:
            target_table = soup.select_one('table[summary*="비고"]')
            if target_table:
                remark_text = target_table.get_text(separator="\n", strip=True)

        # 3. <h3>비  고</h3> 바로 뒤에 오는 테이블 탐색
        if not remark_text:
            for h in soup.find_all(["h3", "h4"]):
                if "비" in h.get_text() and "고" in h.get_text():
                    tbl = h.find_next("table")
                    if tbl:
                        remark_text = tbl.get_text(separator="\n", strip=True)
                        break

        return {
            "remark": remark_text,
            "detail_info": {},
            "raw_content": remark_text
        }

    except Exception as e:
        print(f"  [상세 수집 실패] {detail_url} -> 에러: {e}")
        return {"remark": "", "detail_info": {}, "raw_content": ""}


# 👈 [추가 2] 수집과 AI 파싱을 직렬로 연결한 실행 블록
if __name__ == "__main__":
  print("1. 실시간 공고 목록 수집 중...")
  jobs = fetch_mma_jobs(page_index=1)

  if not jobs:
    print("수집된 공고가 없습니다.")
    exit()

  # 현재 시점 기준 1번째 최신 공고 선택
  target_job = jobs[0]
  print(f"\n2. [실시간 1위 공고 포착]")
  print(f"   - 회사명: {target_job['company']}")
  print(f"   - 제목: {target_job['title']}")
  print(f"   - 링크: {target_job['link']}")

  # 상세 본문(비고란) 긁어오기
  print("\n3. 상세 본문(비고란) 수집 중...")
  detail = fetch_job_detail(target_job["link"])
  raw_remark = detail.get("remark", "")

  # 비고란이 비어있는 일반 공고일 경우 본문 전체 텍스트 활용 (예외 대응)
  if not raw_remark.strip():
    print("비고란이 비어있어 정형 테이블 데이터를 사용합니다.")
    raw_remark = str(detail.get("detail_info", ""))

  # Gemini AI 호출 (실시간 데이터 주입)
  print("\n4. AI가 공고 본문을 정형 JSON으로 분석 중...")
  parsed_json = parse_job_remark_with_ai(target_job["company"], raw_remark)

  print("\n=== 실시간 최신 공고 AI 파싱 최종 결과 ===")
  print(json.dumps(parsed_json, indent=2, ensure_ascii=False))