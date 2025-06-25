import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import platform

# 한글 폰트 설정
if platform.system() == 'Darwin':  # macOS
    font_path = '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
elif platform.system() == 'Windows':
    font_path = 'C:/Windows/Fonts/malgun.ttf'
else:
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

font_name = fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False

# 데이터 불러오기
df = pd.read_csv("data/naver_trends/keyword_trends.tsv", sep='\t')

# 1. 히트맵: 의안번호별 주요 키워드 관심도
# - 각 의안번호별로 키워드 3개 관심도를 행렬로 만들어서 히트맵 그리기

heatmap_df = pd.DataFrame()
for idx, row in df.iterrows():
    bill_no = row['의안번호']
    heatmap_df.at[bill_no, row['주요단어 1']] = row['네이버트렌드 1']
    heatmap_df.at[bill_no, row['주요단어 2']] = row['네이버트렌드 2']
    heatmap_df.at[bill_no, row['주요단어 3']] = row['네이버트렌드 3']

heatmap_df = heatmap_df.fillna(0)

plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_df, annot=True, fmt=".2f", cmap="YlGnBu", cbar_kws={'label': '관심도 점수'})
plt.title("의안번호별 주요 키워드 네이버 트렌드 관심도 히트맵")
plt.ylabel("의안번호")
plt.xlabel("키워드")
plt.tight_layout()
plt.show()


# 2. 의안번호별 네이버트렌드 평균 관심도 막대그래프
plt.figure(figsize=(10, 6))
sns.barplot(data=df, x="의안번호", y="네이버트렌드평균", palette="Blues_d")
plt.title("의안번호별 네이버 트렌드 평균 관심도")
plt.ylabel("평균 관심도")
plt.xlabel("의안번호")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# 3. 키워드별 관심도 분포 박스플롯
df_keywords = pd.DataFrame(columns=["키워드", "관심도"])
for idx, row in df.iterrows():
    for i in range(1, 4):
        kw = row[f'주요단어 {i}']
        score = row[f'네이버트렌드 {i}']
        if pd.notna(kw) and pd.notna(score):
            df_keywords = df_keywords.append({"키워드": kw, "관심도": score}, ignore_index=True)

plt.figure(figsize=(14, 6))
sns.boxplot(data=df_keywords, x="키워드", y="관심도", width=0.9)
plt.title("키워드별 네이버 트렌드 관심도 분포")
plt.ylabel("관심도 점수")
plt.xlabel("키워드")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()