import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import platform

# 1. 한글 폰트 설정
if platform.system() == 'Darwin':
    font_path = '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
elif platform.system() == 'Windows':
    font_path = 'C:/Windows/Fonts/malgun.ttf'
else:
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

font_name = fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False

# 2. 데이터 불러오기
df = pd.read_csv("data/news/news_count.tsv", sep='\t')
df['날짜'] = pd.to_datetime(df['날짜'])

# 3. 시각화 (의안번호 + 키워드 조합으로 hue 설정)
df['의안+키워드'] = df['의안번호'].astype(str) + " - " + df['키워드']

plt.figure(figsize=(14, 7))
sns.lineplot(data=df, x='날짜', y='뉴스건수', hue='의안+키워드', marker='o')

plt.title("의안별 주요 키워드 뉴스 건수 변화 (시계열)")
plt.xlabel("날짜")
plt.ylabel("뉴스 기사 수")
plt.xticks(rotation=45)
plt.legend(title="의안번호 - 키워드", bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.grid(True)
plt.show()