import json
import re
import urllib.parse
from bs4 import BeautifulSoup
import requests

MMA_SEARCH_URL = "https://work.mma.go.kr/caisBYIS/search/cygonggogeomsaek.do"
MMA_BASE_URL = "https://work.mma.go.kr"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": MMA_SEARCH_URL,
    "Content-Type": "application/x-www-form-urlencoded",
}


def fetch_mma_jobs(page_index: int = 1) -> list:
  """병역일터 IT/정보처리 분야 채용공고 목록을 수집합니다."""
  payload = {
      "pageIndex": str(page_index),
      "pageUnit": "10",
      "eopjong_gbcd": "1",  # 1: 정보처리/IT
      "ar_eopjong_gbcd": "11111,11112",
      "eopjong_gbcd_list": "11111,11112",
      "sido_addr": "서울특별시",
      "yeokjong_brcd": "002",  # 보충역/현역
      "ar_bokrihs_cd": "",
      "bokrihs_cd_list": "",
      "gegyumo_cd": "",
      "eopche_nm": "",
      "sigungu_addr": "",
      "cyjemok_nm": "",
      "gyjogeon_cd": "",
  }

  try:
    response = requests.post(
        MMA_SEARCH_URL, headers=HEADERS, data=payload, timeout=10
    )
    response.encoding = response.apparent_encoding or "utf-8"

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
      if len(cols) < 4:
        continue

      # 제목 및 상세 링크 추출
      title_tag = cols[0].find("a")
      title = title_tag.get_text(strip=True) if title_tag else ""
      relative_link = title_tag.get("href", "") if title_tag else ""
      full_link = (
          urllib.parse.urljoin(MMA_BASE_URL, relative_link)
          if relative_link
          else ""
      )

      company = cols[1].get_text(strip=True)
      deadline = cols[2].get_text(strip=True)
      created_at = cols[3].get_text(strip=True) if len(cols) > 3 else ""

      if title and full_link:
        job_list.append({
            "company": company,
            "title": title,
            "deadline": deadline,
            "created_at": created_at,
            "link": full_link,
        })

    return job_list

  except Exception as e:
    print(f"[ERROR] 공고 목록 수집 중 오류 (페이지: {page_index}): {e}")
    return []


def fetch_job_detail(detail_url: str) -> dict:
  """상세 페이지에서 <div class="step1"> 내부의 [비고 사항] 테이블을 정밀 추출합니다."""
  if not detail_url:
    return {"remark": "", "detail_info": {}, "raw_content": ""}

  try:
    response = requests.get(detail_url, headers=HEADERS, timeout=10)
    response.encoding = response.apparent_encoding or "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    # 불필요한 스크립트/스타일 제거
    for tag in soup(["script", "style", "nav", "header", "footer"]):
      tag.decompose()

    remark_text = ""

    # [1순위 타겟] summary 속성에 '비고'가 포함된 테이블 탐색 (공백/글자차이 무관)
    target_table = soup.select_one('table[summary*="비고"]')

    # [2순위 타겟] div.step1 내부에서 '비고' 제목을 가진 구역의 테이블 탐색
    if not target_table:
      for step in soup.select("div.step1"):
        step_header = step.find(["h3", "h4"])
        if step_header and (
            "비" in step_header.get_text() and "고" in step_header.get_text()
        ):
          target_table = step.find("table")
          break

    # [3순위 타겟] caption 태그에 '비고'가 명시된 테이블
    if not target_table:
      for cap in soup.find_all("caption"):
        if "비고" in cap.get_text():
          target_table = cap.find_parent("table")
          break

    # 테이블 내부 전체 텍스트를 줄바꿈 유지하며 추출
    if target_table:
      remark_text = target_table.get_text(separator="\n", strip=True)

    # [Fallback] 비고란이 비어있거나 너무 짧은 특이 공고 대비: 전체 테이블 내용 수집
    detail_info = {}
    all_table_text = []
    for tbl in soup.find_all("table"):
      for row in tbl.find_all("tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
          k = th.get_text(strip=True)
          v = td.get_text(separator=" ", strip=True)
          if k:
            detail_info[k] = v
      t_txt = tbl.get_text(" ", strip=True)
      if t_txt:
        all_table_text.append(t_txt)

    final_content = (
        remark_text
        if (remark_text and len(remark_text) > 20)
        else "\n".join(all_table_text)
    )

    return {
        "remark": final_content,
        "detail_info": detail_info,
        "raw_content": final_content,
    }

  except Exception as e:
    print(f"[ERROR] 상세 페이지 파싱 오류 ({detail_url}): {e}")
    return {"remark": "", "detail_info": {}, "raw_content": ""}


if __name__ == "__main__":
  # 로컬 단독 테스트 실행 블록
  print("1. 실시간 공고 목록 수집 테스트...")
  jobs = fetch_mma_jobs(page_index=1)

  if not jobs:
    print("수집된 공고가 없습니다.")
  else:
    print(f"총 {len(jobs)}건의 공고 포착 완료\n")
    sample = jobs[0]
    print(f"2. [첫 번째 공고 샘플]")
    print(f"   - 회사명: {sample['company']}")
    print(f"   - 제목: {sample['title']}")
    print(f"   - 마감일: {sample['deadline']}")
    print(f"   - 링크: {sample['link']}")

    print("\n3. 상세 본문(비고란) 추출 테스트...")
    detail_data = fetch_job_detail(sample["link"])
    remark = detail_data.get("remark", "")

    print(f"   - 추출된 본문 길이: {len(remark)} 글자")
    print(
        f"   - 본문 미리보기:\n{'-'*40}\n{remark[:300]}...\n{'-'*40}"
        if len(remark) > 300
        else f"   - 본문 전문:\n{remark}"
    )