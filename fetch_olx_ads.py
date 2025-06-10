from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup




OLX_URL = 'https://www.olx.ua/d/uk/list/q-{query}/'  # Шаблон URL для поиска на OLX


def get_olx_ads(query):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Фоновый режим
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(f"https://www.olx.ua/d/uk/list/q-{query.replace(' ', '-')}/")

    
    # Ждем загрузки (можно заменить на ожидание элемента)
    import time
    time.sleep(3)
    
    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.quit()

    ads = {}
    for item in soup.select('div[data-cy="l-card"]'):
        title = item.select_one("h4").get_text(strip=True)
        price = item.select_one('p[data-testid="ad-price"]').get_text(strip=True)
        location_date = item.select_one('p[data-testid="location-date"]').get_text(strip=True)
        link = item.find("a")["href"]
        if 'title' not in ads:
            ads['title'] = []
        if 'price' not in ads:
            ads['price'] = []
        if 'link' not in ads:
            ads['link'] = []
        if 'location_date' not in ads:
            ads['location_date'] = []


        ads['title'].append(title)
        ads['price'].append(str(price))
        ads['location_date'].append(location_date)
        ads['link'].append(link)
    
    return ads