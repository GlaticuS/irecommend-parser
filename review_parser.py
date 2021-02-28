import sys
import requests
from fake_useragent import UserAgent
from itertools import cycle

from bs4 import BeautifulSoup
from random import randint
from time import sleep
from lxml.html import fromstring
import re
import csv


# читаем ввод
filepath_in = sys.argv[1]
filepath_out = sys.argv[2]
use_proxy = sys.argv[3]


result_dict_list = []
def parse_without_proxy(line):
    ua = UserAgent()

    headers = {
        'User-Agent': ua.chrome,
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://irecommend.ru'
    }
    while True:
        try:
            url = 'https://irecommend.ru' + line
            print('processing ', url)
            sleep(randint(8, 11))
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text)

            review_text = soup.find('div', {'itemprop': 'reviewBody'}).text

            review_title = soup.select('h2.reviewTitle a')[0].text

            review_plus_list = soup.select(
                '#content > div.review-node > div.reviewBlock > div.ratio > div.plus > ul')
            review_plus = "\n".join(review_plus_list[0].stripped_strings) if len(review_plus_list) else ''

            review_minus_list = soup.select(
                '#content > div.review-node > div.reviewBlock > div.ratio > div.minus > ul')
            review_minus = "\n".join(review_minus_list[0].stripped_strings) if len(review_minus_list) else ''

            review_verdict_list = soup.select(
                '#content > div.review-node > div.reviewBlock > div.conclusion > span.verdict')
            review_verdict = review_verdict_list[0].text if len(review_verdict_list) else ''

            review_usage_experience_html = soup.find(text='Опыт использования:')
            review_usage_experience = review_usage_experience_html.findNext('div').contents[
                0] if review_usage_experience_html else ''

            review_cost_html = soup.find(text='Стоимость:')
            review_cost = review_cost_html.findNext('div').contents[0] if review_cost_html else ''

            review_raiting = len(soup.select(
                '#content > div.review-node > div.reviewBlock > div.reviewHeader > div.authorBlock > div.text > div.starsRating > div > div > div.on'))

            review_average_rating_list = soup.select(
                'div.rating > div.description > a > div > div > div.description > div > span.average-rating > span')
            sleep(1)
            review_average_rating = review_average_rating_list[0].text if len(review_average_rating_list) else ''

            review_total_votes = soup.find('span', {'class': 'total-votes'}).span.text

            review_category_html = soup.find(text=' Категория:')
            review_category = review_category_html.findNext('a').contents[0] if review_category_html else ''

            review_product_type_html = soup.find(text=' Тип товаров:')
            review_product_type = review_product_type_html.findNext('a').contents[0] if review_product_type_html else ''

            review_user = soup.find('strong', {'class': 'reviewer'}).a.text

            review_user_url = soup.find('a', {'title': 'Информация о пользователе.'}).get('href')
            review_user_url_full = 'https://irecommend.ru' + review_user_url
            sleep(randint(2, 3))
            r_user = requests.get(review_user_url_full, headers=headers)
            user_soup = BeautifulSoup(r_user.text)
            review_user_reviews_count_string_list = user_soup.select(
                '#block-site-0 > div.content.text > div.breadcrumb > div > a')
            review_user_reviews_count_string = review_user_reviews_count_string_list[0].text if len(
                review_user_reviews_count_string_list) else ''
            extract_ints = re.findall(r'\d+', review_user_reviews_count_string)
            review_user_reviews_count = extract_ints[0]

            result = {
                'review_url': url,
                'review_user': review_user,
                'review_user_url': review_user_url_full,
                'review_user_reviews_count': review_user_reviews_count,
                'review_text': review_text,
                'review_title': review_title,
                'review_plus': review_plus,
                'review_minus': review_minus,
                'review_verdict': review_verdict,
                'review_usage_experience': review_usage_experience,
                'review_cost': review_cost,
                'review_raiting': review_raiting,
                'review_average_rating': review_average_rating,
                'review_total_votes': review_total_votes,
                'review_category': review_category,
                'review_product_type': review_product_type
            }
        except Exception as e:
            print(e)
            continue
        break
    return result


# функция для составления пулла прокси
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


def parse_with_proxy(line):
    proxies = get_proxies()
    proxy_pool = cycle(proxies)

    print(proxies)
    proxy = next(proxy_pool)
    while True:
        try:
            url = 'https://irecommend.ru' + line
            print('processing ', url)
            sleep(randint(10, 13))
            r = requests.get(url, proxies={'http': proxy, 'https': proxy})
            soup = BeautifulSoup(r.text)

            review_text = soup.find('div', {'itemprop': 'reviewBody'}).text

            review_title = soup.select('h2.reviewTitle a')[0].text

            review_plus_list = soup.select(
                '#content > div.review-node > div.reviewBlock > div.ratio > div.plus > ul')
            review_plus = review_plus_list[0].text if len(review_plus_list) else ''

            review_minus_list = soup.select(
                '#content > div.review-node > div.reviewBlock > div.ratio > div.minus > ul')
            review_minus = review_minus_list[0].text if len(review_minus_list) else ''

            review_verdict_list = soup.select(
                '#content > div.review-node > div.reviewBlock > div.conclusion > span.verdict')
            review_verdict = review_verdict_list[0].text if len(review_verdict_list) else ''

            review_usage_experience_html = soup.find(text='Опыт использования:')
            review_usage_experience = review_usage_experience_html.findNext('div').contents[
                0] if review_usage_experience_html else ''

            review_cost_html = soup.find(text='Стоимость:')
            review_cost = review_cost_html.findNext('div').contents[0] if review_cost_html else ''

            review_raiting = len(soup.select(
                '#content > div.review-node > div.reviewBlock > div.reviewHeader > div.authorBlock > div.text > div.starsRating > div > div > div.on'))

            review_average_rating_list = soup.select(
                'div.rating > div.description > a > div > div > div.description > div > span.average-rating > span')
            sleep(1)
            review_average_rating = review_average_rating_list[0].text if len(review_average_rating_list) else ''

            review_total_votes = soup.find('span', {'class': 'total-votes'}).span.text

            review_category_html = soup.find(text=' Категория:')
            review_category = review_category_html.findNext('a').contents[0] if review_category_html else ''

            review_product_type_html = soup.find(text=' Тип товаров:')
            review_product_type = review_product_type_html.findNext('a').contents[0] if review_product_type_html else ''

            review_user = soup.find('strong', {'class': 'reviewer'}).a.text

            review_user_url = soup.find('a', {'title': 'Информация о пользователе.'}).get('href')
            review_user_url_full = 'https://irecommend.ru' + review_user_url
            sleep(randint(2, 3))
            proxy = next(proxy_pool)
            r_user = requests.get(review_user_url_full, proxies={'http': proxy, 'https': proxy})
            user_soup = BeautifulSoup(r_user.text)
            review_user_reviews_count_string_list = user_soup.select(
                '#block-site-0 > div.content.text > div.breadcrumb > div > a')
            review_user_reviews_count_string = review_user_reviews_count_string_list[0].text if len(
                review_user_reviews_count_string_list) else ''
            extract_ints = re.findall(r'\d+', review_user_reviews_count_string)
            review_user_reviews_count = extract_ints[0]

            result = {
                'review_url': url,
                'review_user': review_user,
                'review_user_url': review_user_url_full,
                'review_user_reviews_count': review_user_reviews_count,
                'review_text': review_text,
                'review_title': review_title,
                'review_plus': review_plus,
                'review_minus': review_minus,
                'review_verdict': review_verdict,
                'review_usage_experience': review_usage_experience,
                'review_cost': review_cost,
                'review_raiting': review_raiting,
                'review_average_rating': review_average_rating,
                'review_total_votes': review_total_votes,
                'review_category': review_category,
                'review_product_type': review_product_type
            }
        except Exception as e:
            print(e)
            proxy = next(proxy_pool)
            continue
        break
    return result

csv_columns = [
                'review_url',
                'review_user',
                'review_user_url',
                'review_user_reviews_count',
                'review_text',
                'review_title',
                'review_plus',
                'review_minus',
                'review_verdict',
                'review_usage_experience',
                'review_cost',
                'review_raiting',
                'review_average_rating',
                'review_total_votes',
                'review_category',
                'review_product_type'
              ]


with open(filepath_in, 'r') as fp, open(filepath_out, 'a') as fout:
    writer = csv.DictWriter(fout, fieldnames=csv_columns)
    writer.writeheader()

    line = fp.readline()

    while line:
        if use_proxy == 'yes':
            result = parse_with_proxy(line)
        else:
            result = parse_without_proxy(line)

        writer.writerow(result)
        line = fp.readline()



