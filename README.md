# Job_Finder (병역일터 AI 채용 분석 파이프라인)

병무청 병역일터 채용공고를 자동으로 수집·정제하고, LLM을 통해 기술 스택과 지원 요건을 구조화하여 맞춤형 알림을 제공하는 데이터 파이프라인 프로젝트입니다.

## Tech Stack

아직 미정...

- **Language**: Python 3.x
- **Crawler**: Requests, BeautifulSoup4 (또는 Playwright)
- **AI/LLM**: Gemini API / Structured Outputs
- **Database**: SQLite / PostgreSQL


# 환경설정 가이드라인 및 진행 내용들

병역일터(MMA) 지능형 채용 공고 수집 및 LLM 기반 파싱 에이전트 개발 환경 설정 가이드입니다.

---

## 1. 사전 요구사항 (Prerequisites)

* **Python 3.10** 이상
* **Google AI Studio** 계정 및 API Key ([Google AI Studio 바로가기](https://aistudio.google.com/))

---

## 2. 환경 설정 및 패키지 설치 (Installation)

### ① 가상환경 생성 및 활성화
프로젝트 격리를 위해 가상환경(venv)을 생성하고 활성화합니다.

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화 (macOS / Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows PowerShell)
# .\venv\Scripts\Activate.ps1

--

pip install requests beautifulsoup4 google-genai python-dotenv

--

pip freeze > requirements.txt
# 이후 협업 환경에서는 `pip install -r requirements.txt`로 일괄 설치 가능
# 아직 진행하지 않았음
--

env 파일에 api코드 설정 완료하였음
gitignore 설정 완료하였음

--


1차 파이프 라인 완성 이루 데이터 베이스 구축시작

------------------------

