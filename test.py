import os
import psycopg2
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)

url = 'https://youtube.cosmswss'
with conn.cursor() as curs:
    curs.execute(f"SELECT * FROM test")
    all_users = curs.fetchall()[::-1]

for item in all_users:
    print(item)
