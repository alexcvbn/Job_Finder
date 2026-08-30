import json
import sqlite3
from urllib.parse import parse_qs, urlparse

DB_PATH = "mma_jobs.db"


def get_connection():
  """데이터베이스 커넥션 객체를 반환합니다."""
  return sqlite3.connect(DB_PATH)


def init_db():
  """테이블이 없으면 새로 생성합니다."""
  with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_no TEXT PRIMARY KEY,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                deadline TEXT,
                link TEXT,
                recruit_types TEXT,
                positions TEXT,
                tech_stacks TEXT,
                apply_url TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.commit()


def extract_job_no(url):
  """URL 쿼리스트링에서 공고 고유 번호(cygonggo_no)를 추출합니다."""
  parsed = urlparse(url)
  params = parse_qs(parsed.query)
  return params.get("cygonggo_no", [None])[0]


def is_job_exists(job_no):
  """해당 공고가 이미 DB에 저장되어 있는지 확인합니다 (중복 방지)."""
  if not job_no:
    return False

  with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM jobs WHERE job_no = ? LIMIT 1", (str(job_no),)
    )
    return cursor.fetchone() is not None


def save_job(meta_job, parsed_ai_data):
  """메타 정보와 AI 분석 결과를 DB에 영구 저장합니다."""
  job_no = extract_job_no(meta_job["link"])
  if not job_no:
    return False

  with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
        """
            INSERT OR IGNORE INTO jobs (
                job_no, company, title, deadline, link,
                recruit_types, positions, tech_stacks, apply_url, summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job_no,
            meta_job.get("company", ""),
            meta_job.get("title", ""),
            meta_job.get("deadline", ""),
            meta_job.get("link", ""),
            json.dumps(
                parsed_ai_data.get("recruit_types", []), ensure_ascii=False
            ),
            json.dumps(parsed_ai_data.get("positions", []), ensure_ascii=False),
            json.dumps(
                parsed_ai_data.get("tech_stacks", []), ensure_ascii=False
            ),
            parsed_ai_data.get("apply_url"),
            parsed_ai_data.get("summary", ""),
        ),
    )
    conn.commit()
    return True


if __name__ == "__main__":
  init_db()