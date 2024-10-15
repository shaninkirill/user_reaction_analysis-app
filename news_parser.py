import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MONTHS = {
    'янв': '01', 'фев': '02', 'мар': '03', 'апр': '04', 'май': '05', 'июн': '06',
    'июл': '07', 'авг': '08', 'сен': '09', 'окт': '10', 'ноя': '11', 'дек': '12'
}


embedding_model = SentenceTransformer('sergeyzh/rubert-tiny-turbo')


def cosine_similarity_check(query_embedding, title_embedding, threshold=0.8):
    similarity = cosine_similarity([query_embedding], [title_embedding])[0][0]

    return similarity >= threshold


def extract(search_query: str, news_count: int) -> None:
    chrome_options = Options()
    chrome_options.add_argument("--headless=old")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-extensions")


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        search_url = f"https://www.rbc.ru/search/?query={search_query}"
        driver.get(search_url)

        time.sleep(2)

        news_data = []
        titles_seen = set()
        current_year = datetime.now().year

        date_pattern = re.compile(r'(\d{1,2})\s(\w{3})\s*(\d{4})?,\s*(\d{2}:\d{2})')

        last_height = driver.execute_script("return document.body.scrollHeight")

        query_embedding = embedding_model.encode(search_query.lower())

        while len(news_data) < news_count:
            news_blocks = driver.find_elements(By.CLASS_NAME, 'search-item')

            for news_block in news_blocks[len(news_data):]:
                title_element = news_block.find_element(By.CLASS_NAME, 'search-item__title')
                title = title_element.text

                if title in titles_seen:
                    continue

                title_embedding = embedding_model.encode(title.lower())

                if not cosine_similarity_check(query_embedding, title_embedding):
                    continue

                try:
                    text_element = news_block.find_element(By.CLASS_NAME, 'search-item__text')
                    text = text_element.text
                except:
                    text = ''

                try:
                    date_element = news_block.find_element(By.CLASS_NAME, 'search-item__category').text.strip()

                    match = date_pattern.search(date_element)

                    day = match.group(1)
                    month_str = match.group(2)
                    year = match.group(3) if match.group(3) else str(current_year)

                    month = MONTHS.get(month_str.lower(), '01')

                    date = f"{day}.{month}.{year}"

                except:
                    current_year = datetime.now().year
                    current_date = datetime.now().strftime("%d.%m.%Y")
                    date = current_date

                titles_seen.add(title)

                try:
                    link_element = news_block.find_element(By.CLASS_NAME, 'search-item__link')
                    link = link_element.get_attribute('href')
                except:
                    link = ''

                news_data.append({
                    "title": title,
                    "text": text,
                    "date": date,
                    "link": link
                })

                if len(news_data) >= news_count:
                    break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break

            last_height = new_height

        news_json = json.dumps(news_data[:news_count], ensure_ascii=False, indent=4)

        with open('news.json', 'w', encoding='utf-8') as json_file:
            json_file.write(news_json)

    finally:
        driver.quit()