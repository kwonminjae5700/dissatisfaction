import os
import time
import re
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 경로 설정
DOWNLOAD_DIR = os.path.abspath("data/bill/pdf")
TSV_PATH = os.path.abspath("data/bill/data.tsv")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def configure_driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("user-agent=Mozilla/5.0 ... Safari/537.36")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    return webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=chrome_options)

def wait_for_new_file(before_files, timeout=15):
    for _ in range(timeout * 2):
        time.sleep(0.5)
        after_files = set(os.listdir(DOWNLOAD_DIR))
        new_files = list(after_files - set(before_files))
        if new_files:
            return os.path.join(DOWNLOAD_DIR, new_files[0])
    return ""

def main():
    driver = configure_driver()
    results = []

    try:
        driver.get('https://likms.assembly.go.kr/bill/LatestPassedBill.do')
        print("페이지 접속")

        tbody = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.tableCol01 table tbody"))
        )

        for page in range(1, 2):
            print(f"페이지 {page} 처리 중...")
            rows = tbody.find_elements(By.TAG_NAME, "tr")

            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) < 7:
                    continue

                bill_number = cols[0].text.strip()
                bill_name = cols[1].text.strip()
                proposal_date = cols[3].text.strip()
                resolution_date = cols[5].text.strip()

                # billId 추출
                bill_id = None
                try:
                    href = cols[1].find_element(By.TAG_NAME, 'a').get_attribute('href')
                    match = re.search(r"fGoDetail\('([^']+)'", href)
                    if match:
                        bill_id = match.group(1)
                except:
                    pass

                pdf_path = ""
                detail_url = ""

                if bill_id:
                    detail_url = f"https://likms.assembly.go.kr/bill/billDetail.do?billId={bill_id}"
                    driver.execute_script(f"window.open('{detail_url}', '_blank');")
                    driver.switch_to.window(driver.window_handles[-1])

                    try:
                        # 상세 페이지 로딩
                        detail_tbody = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.contIn div.tableCol01 table tbody"))
                        )
                        detail_row = detail_tbody.find_element(By.TAG_NAME, "tr")
                        detail_cols = detail_row.find_elements(By.TAG_NAME, "td")

                        before_files = os.listdir(DOWNLOAD_DIR)
                        pdf_clicked = False

                        for a in detail_cols[3].find_elements(By.CSS_SELECTOR, "a"):
                            try:
                                img = a.find_element(By.TAG_NAME, "img")
                                if "pdf" in img.get_attribute("src").lower():
                                    a.click()
                                    pdf_clicked = True
                                    break
                            except:
                                continue

                        if pdf_clicked:
                            pdf_path = wait_for_new_file(before_files)
                    except Exception as e:
                        print(f"상세페이지 오류: {e}")

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                results.append({
                    "의안번호": bill_number,
                    "의안명": bill_name,
                    "제안일자": proposal_date,
                    "의결일자": resolution_date,
                    "상세페이지 URL": detail_url,
                    "PDF 파일 경로": pdf_path,
                })

                time.sleep(1)

            # 페이지 이동
            if page < 10:
                try:
                    next_btn = driver.find_element(By.LINK_TEXT, str(page + 1))
                    next_btn.click()
                    time.sleep(2)
                    tbody = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.tableCol01 table tbody"))
                    )
                except Exception as e:
                    print(f"다음 페이지 이동 실패: {e}")
                    break

    finally:
        driver.quit()
        print("드라이버 종료")

        # TSV 저장
        os.makedirs(os.path.dirname(TSV_PATH), exist_ok=True)
        with open(TSV_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys(), delimiter="\t")
            writer.writeheader()
            writer.writerows(results)

        print(f"총 {len(results)}개 데이터 저장 완료")

if __name__ == "__main__":
    main()