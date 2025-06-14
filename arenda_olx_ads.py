from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/q-%D0%B0%D1%80%D0%B5%D0%BD%D0%B4%D0%B0-%D0%BA%D0%B2%D0%B0%D1%80%D1%82%D0%B8%D1%80%D1%8B/?search%5Bdistrict_id%5D=17&search%5Border%5D=filter_float_price:asc&search%5Bfilter_float_price:from%5D=300&currency=USD
OLX_URL = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/{city}/q-%D0%B0%D1%80%D0%B5%D0%BD%D0%B4%D0%B0-%D0%BA%D0%B2%D0%B0%D1%80%D1%82%D0%B8%D1%80%D1%8B/?search%5Bdistrict_id%5D=17&search%5Border%5D={sort}&search%5Bfilter_float_price:from%5D=300&currency={currency}'  # Шаблон URL для поиска на OLX
city_list = {
    "киев": "kiev",
    "днепр": "dnepr",
    "одесса": "odessa",
    "харьков": "kha",              
    "львов": "lvov",
    "запорожье": "zaporozhe",    
    "чернигов": "chernigov",
    "винница": "vinnitsa",
    "полтава": "poltava",
    "ужгород": "uzhgorod",
    "тернополь": "ternopol",
    "ивано-франковск": "if",
    "черновцы": "chernovtsy",
    "хмельницкий": "khmelnitskiy", 
    "житомир": "zhitomir",
    "черкассы": "cherkassy",
    "кривой рог": "krivoyrog",
    "мариуполь": "mariupol",
    "луцк": "lutsk",  
    "ровно": "rovno"
}


def get_olx_arenda(city, sort, currency):
    """ Получение get запроса с сайта olx по объявлением о сдаче квартир """
    url = OLX_URL.format(city=city, sort=sort, currency=currency)

    if sort == '1' or sort == 'от дешёвых к дорогим': sort = 'filter_float_price:asc'
    if sort == '2' or sort == 'от дорогих к дешёвым': sort = 'filter_float_price:desc'
    if sort == '3' or sort == 'рекомендованные': sort = 'relevance:desc'
    if sort == None: sort = 'relevance:desc'

    if currency == None: currency = 'USD'
    if currency.upper() == 'USD' or currency.upper() == 'ЮСД': currency = 'USD'
    if currency.upper() == 'UAH' or currency.upper() == 'ЮАН': currency = 'UAH'

    valid_city = False
    for c in city_list:
        if city == c:
            valid_city = True
            city = city_list[c]
            break
    
    if valid_city == False: return print('неверно указан город')


    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Фоновый режим
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(f"https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/{city}/q-%D0%B0%D1%80%D0%B5%D0%BD%D0%B4%D0%B0-%D0%BA%D0%B2%D0%B0%D1%80%D1%82%D0%B8%D1%80%D1%8B/?search%5Bdistrict_id%5D=17&search%5Border%5D={sort}&search%5Bfilter_float_price:from%5D=300&currency={currency}")

    # Ждем загрузки (можно заменить на ожидание элемента)
    import time
    time.sleep(5)
    
    soup = BeautifulSoup(driver.page_source, "lxml")

    ads = {}

    if 'title' not in ads: ads['title'] = []
    if 'price' not in ads: ads['price'] = []
    if 'link' not in ads: ads['link'] = []
    if 'location_date' not in ads: ads['location_date'] = []
    if 'city' not in ads: ads['city'] = []

    try:
        driver.get(url)
        for item in soup.select('div[data-cy="l-card"]'):
            title = item.select_one("h4").get_text(strip=True)
            price = item.select_one('p[data-testid="ad-price"]').get_text(strip=True)
            location_date = item.select_one('p[data-testid="location-date"]').get_text(strip=True)
            link = item.find("a")["href"]

            ads['title'].append(title)
            ads['price'].append(str(price))
            ads['location_date'].append(location_date)
            ads['link'].append(link)
            ads['city'].append(city)

        return ads
    finally:
        driver.quit()
