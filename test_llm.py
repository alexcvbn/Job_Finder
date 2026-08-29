# llm 연결 확인하는 테스트 프로그램
import os
from dotenv import load_dotenv
from google import genai

# 1. .env 파일에 저장된 환경 변수를 운영체제 메모리로 로드
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
  print("ERROR: .env 파일에서 api키를 찾을 수 없음")
  exit()

# 2. 클라이언트 초기화 (신분증 등록) (요건 아직)
client = genai.Client(api_key=api_key)

# 3. 모델로 테스트
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="안녕 너와 정상적으로 연결되었는지 한 문장으로 대답해줘.",
)

print("\nGemini 응답:")
print(response.text)