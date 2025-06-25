import os
import pdfplumber
from mecab import MeCab
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

PDF_DIR = "data/bill/pdf"
OUTPUT_TSV = "data/bill/pdf_keywords.tsv"
TOP_N_KEYWORDS = 3

tagger = MeCab()

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() or ''
            return text.strip()
    except Exception as e:
        print(f"오류: {file_path} - {e}")
        return ''

def tokenize(text):
    # 명사만 추출 (N으로 시작하는 품사)
    return [word for word, pos in tagger.pos(text) if pos.startswith('N')]

pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]

documents = []
valid_filenames = []

for pdf_file in pdf_files:
    pdf_path = os.path.join(PDF_DIR, pdf_file)
    text = extract_text_from_pdf(pdf_path)
    if text:
        tokens = tokenize(text)
        if tokens:
            documents.append(' '.join(tokens))
            valid_filenames.append(pdf_file)
        else:
            print(f"명사 추출 실패: {pdf_file}")
    else:
        print(f"텍스트 추출 실패 또는 비어 있음: {pdf_file}")

if not documents:
    print("분석할 문서가 없습니다.")
    exit()

vectorizer = TfidfVectorizer(
    max_df=0.95,
    min_df=2,  # 최소 2문서 이상 등장하는 단어만
)
tfidf_matrix = vectorizer.fit_transform(documents)
terms = vectorizer.get_feature_names_out()

result_data = []
for i, row in enumerate(tfidf_matrix):
    row_data = row.toarray().flatten()
    top_indices = row_data.argsort()[-TOP_N_KEYWORDS:][::-1]
    keywords = [terms[idx] for idx in top_indices]
    bill_number = valid_filenames[i][:7]  # 파일명 앞 7글자 -> 의안번호
    result_data.append([bill_number] + keywords)

os.makedirs(os.path.dirname(OUTPUT_TSV), exist_ok=True)
columns = ['의안번호'] + [f'주요단어 {i+1}' for i in range(TOP_N_KEYWORDS)]
df = pd.DataFrame(result_data, columns=columns)
df.to_csv(OUTPUT_TSV, sep='\t', index=False, encoding='utf-8')

print(f"총 {len(result_data)}개 PDF에 대해 키워드 추출 완료: {OUTPUT_TSV}")