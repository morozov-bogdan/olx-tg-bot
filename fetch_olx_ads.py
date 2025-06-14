from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager


OLX_URL = 'https://www.olx.ua/d/uk/list/q-{query}/'  # Шаблон URL для поиска на OLX

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Фоновый режим
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)



def get_olx_ads(query, offset=0, limit=20):
    """ Получение get запроса с сайта olx по поисковым запросам """

    driver = create_driver()
    driver.get(f"https://www.olx.ua/d/uk/list/q-{query.replace(' ', '-')}/?page={offset // limit + 1}")
    

    try:
        # Ждем до 10 секунд пока не появится элемент с css-селектором '[data-cy="l-card"]'
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="l-card"]'))
        )
    except:
        print("Элемент не найден")
        driver.quit()
    

    soup = BeautifulSoup(driver.page_source, "lxml")
    ads = {'title': [], 'price': [], 'link': [], 'location_date': []}
    items = soup.select('div[data-cy=l-card]')[offset % limit : offset % limit + limit]

    try:
        for item in items:
            try:
                title = item.select_one("h4").get_text(strip=True)
                price = item.select_one('p[data-testid="ad-price"]').get_text(strip=True)
                location_date = item.select_one('p[data-testid="location-date"]').get_text(strip=True)
                link = item.find("a")["href"] 
            except:
                if title == None: title = 'Нету название'
                if price == None: price = 'Цена не указана'
                if location_date == None: location_date = 'Локация не указана'
                if link == None: link = 'К сожалению не получилось получить ссылку'

            ads['title'].append(title)
            ads['price'].append(str(price))
            ads['location_date'].append(location_date)
            ads['link'].append(link)
    finally:
        driver.quit()
    
    return ads