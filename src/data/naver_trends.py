import requests
import json
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# --- 설정 ---
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

TSV_PATH = "data/bill/pdf_keywords.tsv"
OUTPUT_PATH = "data/naver_trends/keyword_trends.tsv"

START_DATE = (datetime.today() - timedelta(days=60)).strftime("%Y-%m-%d")
END_DATE = datetime.today().strftime("%Y-%m-%d")
TIMEUNIT = "date"

# --- 네이버 데이터랩 API 요청 함수 ---
def get_naver_trend_single(keyword: str) -> float:
    if not keyword or keyword.strip() == '':
        raise ValueError("빈 키워드입니다.")

    url = "https://openapi.naver.com/v1/datalab/search"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json",
    }
    body = {
        "startDate": START_DATE,
        "endDate": END_DATE,
        "timeUnit": TIMEUNIT,
        "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}],
        "device": "",
        "ages": [],
        "gender": ""
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body, ensure_ascii=False).encode('utf-8'))
    resp.raise_for_status()
    data = resp.json()

    if "results" not in data or not data["results"]:
        raise ValueError("데이터랩 결과 없음")

    data_points = data["results"][0].get("data", [])
    if not data_points:
        raise ValueError("관심도 데이터 없음")

    values = [float(dp.get("ratio", 0)) for dp in data_points]
    if not values:
        raise ValueError("관심도 값이 비어있음")

    return sum(values) / len(values)

# --- 메인 처리 ---
def main():
    df = pd.read_csv(TSV_PATH, sep='\t')

    for idx, row in df.iterrows():
        bno = row['의안번호']
        keywords = [row.get(f'주요단어 {i}', '') for i in range(1, 6)]
        scores = []

        for i, kw in enumerate(keywords, start=1):
            if isinstance(kw, str) and kw.strip() != '':
                try:
                    score = round(get_naver_trend_single(kw), 2)
                    df.loc[idx, f'네이버트렌드 {i}'] = score
                    scores.append(score)
                    print(f"✅ {bno} - {kw}: {score}")
                except Exception as e:
                    df.loc[idx, f'네이버트렌드 {i}'] = 0.0
                    print(f"❌ {bno} - {kw}: 오류 발생 - {e}")
            else:
                df.loc[idx, f'네이버트렌드 {i}'] = 0.0

        mean_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        df.loc[idx, '네이버트렌드평균'] = mean_score

    # TSV 저장
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, sep='\t', index=False, encoding='utf-8')
    print(f"\n✅ 저장 완료: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()