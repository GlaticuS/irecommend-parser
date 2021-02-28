import requests
import sys
from fake_useragent import UserAgent
from itertools import cycle

from bs4 import BeautifulSoup
from random import randint
from time import sleep

from lxml.html import fromstring


# функция для формирования списка прокси с сайта бесплатных прокси. берем только те, которые поддерживают https
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:50]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies



# считываем входные данные
url_in = sys.argv[1]
pages = sys.argv[2]
filename = sys.argv[3]
use_proxy = sys.argv[4]

ua = UserAgent()

headers = {
    'User-Agent': ua.chrome,
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://irecommend.ru'
}

# парсинг тут
if use_proxy == 'yes':
    for i in range(0, int(pages)):
        # Get a proxy from the pool
        print("Request #%d" % i)
        # вечный цикл для того, чтобы несколько раз пытаться связаться с одним url'ом - при плохом прокси может вылезти ошибка, тогда меняем прокси
        while True:
            try:
                url = url_in + '?page=' + str(i)
                print(url)
                sleep(randint(8, 13))
                r = requests.get(url, headers=headers)
                soup = BeautifulSoup(r.text)
                review_href = soup.findAll('a', {"class": "more"})
                for elem in review_href:
                    print('processing href...')
                    elemHref = elem.get('href')
                    with open(filename, 'a') as output_file:
                        output_file.write(elemHref + '\n')
            except Exception as e:
                # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
                # We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
                print(e)
                continue
            break
else:
    proxies = get_proxies()
    proxy_pool = cycle(proxies)
    print(proxies)

    for i in range(0, int(pages)):
        # Get a proxy from the pool
        proxy = next(proxy_pool)
        print("Request #%d" % i)
        # вечный цикл для того, чтобы несколько раз пытаться связаться с одним url'ом - при плохом прокси может вылезти ошибка, тогда меняем прокси
        while True:
            try:
                url = url_in + '?page=' + str(i)
                print(url)
                sleep(randint(8, 13))
                r = requests.get(url, proxies={"http": proxy, "https": proxy})
                soup = BeautifulSoup(r.text)
                review_href = soup.findAll('a', {"class": "more"})
                for elem in review_href:
                    print('processing href...')
                    elemHref = elem.get('href')
                    with open(filename, 'a') as output_file:
                        output_file.write(elemHref + '\n')
            except Exception as e:
                # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
                # We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
                print(e)
                proxy = next(proxy_pool)
                continue
            break
