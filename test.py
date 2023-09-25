import os
import psycopg2
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)

with conn.cursor() as curs:
    query = 'SELECT url_id, MAX(b.created_at) AS last_tested_at' \
            ' FROM urls a' \
            ' INNER JOIN url_checks b ON a.id = b.url_id' \
            ' GROUP BY url_id' \
            ' ORDER BY url_id;'
    curs.execute(query)
    result = curs.fetchall()

checks = {}
for item in result:
    checks[item[0]] = item[1]

print(checks)


