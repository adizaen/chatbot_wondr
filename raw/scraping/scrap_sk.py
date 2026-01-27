from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import re
import time

URL = "https://wondr.bni.co.id/info/terms-conditions"
OUTPUT_FILE = "../output/sk_wondr.json"


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def scrape_terms_conditions():
    # =========================
    # 1. SETUP BROWSER
    # =========================
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(URL)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    editor = soup.select_one(".ql-editor")
    if not editor:
        raise RuntimeError("Konten S&K (.ql-editor) tidak ditemukan")

    # =========================
    # 2. INIT
    # =========================
    document = {
        "document": "Syarat dan Ketentuan wondr by BNI",
        "source_url": URL,
        "sections": []
    }

    current_section = None
    current_clause = None
    current_sub = None

    # =========================
    # 3. PARSE
    # =========================
    for el in editor.find_all(["p", "ol"]):

        text = clean_text(el.get_text(" ", strip=True))
        if not text:
            continue

        # ---- PASAL ----
        m_section = re.match(r"^(\d{1,2})\.\s+([A-Z\s\-()]+)$", text)
        if m_section:
            current_section = {
                "section_number": m_section.group(1),
                "title": m_section.group(2),
                "clauses": []
            }
            document["sections"].append(current_section)
            current_clause = None
            current_sub = None
            continue

        # ---- AYAT (a. b.) ----
        m_clause = re.match(r"^([a-z]{1,2})\.\s+(.*)", text)
        if m_clause and current_section:
            current_clause = {
                "code": f"{current_section['section_number']}.{m_clause.group(1)}",
                "level": m_clause.group(1),
                "text": m_clause.group(2)
            }
            current_section["clauses"].append(current_clause)
            current_sub = None
            continue

        # ---- SUB AYAT (1) 2)) ----
        m_sub = re.match(r"^(\d+)\)\s+(.*)", text)
        if m_sub and current_clause:
            current_sub = {
                "code": f"{current_clause['code']}.{m_sub.group(1)}",
                "level": m_sub.group(1),
                "text": m_sub.group(2)
            }
            current_clause.setdefault("subclauses", []).append(current_sub)
            continue

        # ---- ROMAWI (i. ii.) → SELALU sub dari angka ----
        m_roman = re.match(r"^([ivxlcdm]+)\.\s+(.*)", text)
        if m_roman and current_sub:
            current_sub.setdefault("items", []).append({
                "level": m_roman.group(1),
                "text": m_roman.group(2)
            })
            continue

        # ---- LIST <ol> ----
        if el.name == "ol" and current_clause:
            for li in el.find_all("li"):
                current_clause.setdefault("subclauses", []).append({
                    "level": "list",
                    "text": clean_text(li.get_text(" ", strip=True))
                })
            continue

        # ---- LANJUTAN TEKS ----
        if current_sub:
            current_sub["text"] += " " + text
        elif current_clause:
            current_clause["text"] += " " + text

    # =========================
    # 4. CLEAN EMPTY SUBCLAUSES
    # =========================
    for sec in document["sections"]:
        for cl in sec["clauses"]:
            if "subclauses" in cl and not cl["subclauses"]:
                del cl["subclauses"]

    # =========================
    # 5. SAVE JSON
    # =========================
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(document, f, indent=2, ensure_ascii=False)

    print("✅ Scraping berhasil")
    print(f"📄 Total Pasal: {len(document['sections'])}")
    print(f"💾 File disimpan: {OUTPUT_FILE}")


if __name__ == "__main__":
    scrape_terms_conditions()
