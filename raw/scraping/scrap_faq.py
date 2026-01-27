from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time

URL = "https://wondr.bni.co.id/info/faq"
OUTPUT_FILE = "../output/faq_all_categories.json"


def scrape_all_categories():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")  # FIX UTAMA
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(URL)
    wait = WebDriverWait(driver, 20)

    # tunggu kategori desktop muncul
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "button.hidden.md\\:block")
    ))

    all_data = []

    category_count = len(
        driver.find_elements(By.CSS_SELECTOR, "button.hidden.md\\:block")
    )

    print(f"🔎 Total kategori ditemukan: {category_count}")

    for i in range(category_count):
        categories = driver.find_elements(
            By.CSS_SELECTOR, "button.hidden.md\\:block"
        )

        btn = categories[i]
        category_name = btn.text.strip()

        driver.execute_script("arguments[0].click();", btn)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        faq_items = soup.select("div.faq-item")

        for faq in faq_items:
            q = faq.select_one("div.ql-content.ql-editor")
            question = q.get_text(strip=True) if q else None

            a = faq.select_one("div.faq-content div.ql-content.ql-editor")
            answer = a.get_text(separator="\n", strip=True) if a else None

            if question:
                all_data.append({
                    "category": category_name,
                    "question": question,
                    "answer": answer
                })

        print(f"✔ {category_name}: {len(faq_items)} FAQ")

    driver.quit()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print("\n✅ SELESAI")
    print(f"📁 File: {OUTPUT_FILE}")
    print(f"📊 Total FAQ: {len(all_data)}")


if __name__ == "__main__":
    scrape_all_categories()
