from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

OLX_URL = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/{city}/q-аренда-квартиры/?currency={currency}&page={page}&search%5Border%5D={sort}'  # Шаблон URL для поиска на OLX
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

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Фоновый режим
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def get_olx_arenda(city, currency=None, sort=None, min_price=None, max_price=None,offset=0, limit=20):
    """ Получение get запроса с сайта olx по объявлением о сдаче квартир """
    url = OLX_URL.format(city=city, currency=currency, sort=sort, page={offset // limit + 1})

    if sort == '1' or sort == 'от дешёвых к дорогим': sort = 'filter_float_price:asc'
    if sort == '2' or sort == 'от дорогих к дешёвым': sort = 'filter_float_price:desc'
    if sort == '3' or sort == 'рекомендованные': sort = 'relevance:desc'
    if sort == None: sort = 'relevance:desc'

    if currency == None: currency = 'USD'
    if currency.upper() == 'USD' or currency.upper() == 'ЮСД': currency = 'USD'
    if currency.upper() == 'UAH' or currency.upper() == 'ЮАН': currency = 'UAH'

    if isinstance(min_price, int): f'&search%5Bfilter_float_price:from%5D={str(min_price)}'
    if isinstance(max_price, int): f'&search%5Bfilter_float_price:to%5D={str(max_price)}'
    if isinstance(min_price, int) or isinstance(max_price, int): 
        if min_price > max_price: 
             print('Минимальное число больше максимального, требуется ввести корректно')
             return

    valid_city = False
    for c in city_list:
        if city == c:
            valid_city = True
            city = city_list[c]
            break
    
    if valid_city == False: return print('неверно указан город')


    driver = create_driver()
    driver.get(f"https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/{city}/q-аренда-квартиры/?currency={currency}")
    # Ждем загрузки (можно заменить на ожидание элемента)
    import time
    time.sleep(5)
    
    soup = BeautifulSoup(driver.page_source, "lxml")

    ads = {'title': [], 'price': [], 'link': [], 'location_date': [], 'city': []}
    items = soup.select('div[data-cy=l-card]')[offset % limit : offset % limit + limit]

    try:
        driver.get(url)
        for item in items:
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
