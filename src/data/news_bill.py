import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

# 환경변수 로드
load_dotenv()
NEWS_URL = os.getenv("NEWS_URL")

# 입력, 출력 경로
INPUT_TSV = "data/bill/pdf_keywords.tsv"
OUTPUT_TSV = "data/news/news_count.tsv"

# 날짜 범위 설정
START_DATE = datetime(2025, 5, 25)
END_DATE = datetime.today()

# NewsAPI 엔드포인트
NEWS_API_URL = "https://newsapi.org/v2/everything"

# 의안번호별 1순위 키워드 가져오기
df = pd.read_csv(INPUT_TSV, sep='\t')

# 중복된 의안번호가 있으면 대표 1개만 쓰기 (필요시 변경 가능)
df_unique = df.drop_duplicates(subset=['의안번호'])

results = []

def daterange(start_date, end_date):
    """날짜 범위 generator, 하루씩 증가"""
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(n)

# 각 의안번호별 주요단어1에 대해 날짜별 뉴스기사 수 조회
for idx, row in df_unique.iterrows():
    bill_no = row['의안번호']
    keyword = row['주요단어 1']
    if pd.isna(keyword) or str(keyword).strip() == "":
        continue
    keyword = str(keyword).strip()
    
    print(f"🔎 처리 시작 - 의안번호: {bill_no}, 키워드: {keyword}")
    
    for single_date in daterange(START_DATE, END_DATE):
        from_date = single_date.strftime("%Y-%m-%d")
        to_date = single_date.strftime("%Y-%m-%d")
        
        params = {
            "q": keyword,
            "from": from_date,
            "to": to_date,
            "sortBy": "publishedAt",
            "language": "ko",      # 한국어 기사만 (필요시 제거)
            "pageSize": 1,         # 건수만 필요하므로 1개만 요청
            "page": 1,
        }
        
        try:
            response = requests.get(NEWS_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            total_results = data.get("totalResults", 0)
            results.append({
                "의안번호": bill_no,
                "키워드": keyword,
                "날짜": from_date,
                "뉴스건수": total_results
            })
            
            print(f"  {from_date}: {total_results}건")
            
        except Exception as e:
            print(f"❌ 오류 발생 - 의안번호: {bill_no}, 날짜: {from_date}, 에러: {e}")
        
        time.sleep(1)  # API 호출 제한 대비 딜레이
    
# 결과를 DataFrame으로 변환 후 저장
df_results = pd.DataFrame(results)
os.makedirs(os.path.dirname(OUTPUT_TSV), exist_ok=True)
df_results.to_csv(OUTPUT_TSV, sep='\t', index=False, encoding='utf-8')

print(f"\n✅ 작업 완료, 결과 저장: {OUTPUT_TSV}")