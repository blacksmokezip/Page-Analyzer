# import os
# import psycopg2
# from dotenv import load_dotenv, find_dotenv
#
# load_dotenv(find_dotenv())
#
# DATABASE_URL = os.environ.get('DATABASE_URL')
#
# conn = psycopg2.connect(DATABASE_URL)
#
# with conn.cursor() as curs:
#     query = 'SELECT a.id, MAX(b.created_at) AS last_tested_at' \
#             ' FROM urls a' \
#             ' INNER JOIN url_checks b ON a.id = b.url_id' \
#             ' GROUP BY a.id' \
#             ' ORDER BY a.id;'
#     curs.execute(query)
#     result = curs.fetchall()
#
# checks = {}
# for item in result:
#     print(item)
#
# print(checks)
#
# with conn.cursor() as cur:
#     cur.execute("SELECT * FROM urls")
#     urls = cur.fetchall()[::-1]
#     for item in urls:
#         print(item[0])
import requests
from bs4 import BeautifulSoup

url = 'https://bootstrap-4.ru'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
h1 = soup.find('h1')
title = soup.find('title')
meta_tag = soup.find('meta', {'name': 'description'})
if h1:
    print(h1.text)
if title:
    print(title.text)
if meta_tag:
    content = meta_tag['content']
    print(content)
else:
    print('Тег <meta name="description"> не найден на странице.')