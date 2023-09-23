from flask import Flask, render_template, request, flash, redirect, url_for
import os
import psycopg2
from dotenv import load_dotenv, find_dotenv
from datetime import date
from urllib.parse import urlparse

load_dotenv(find_dotenv())

DATABASE_URL = os.environ.get('DATABASE_URL')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


@app.route('/')
def main_page():
    return render_template(
        'index.html'
    )

@app.post('/urls')
def post_urls():
    url = request.form.to_dict()['url']

    error = validate(url)

    if error:
        flash(error)
        return render_template(
            'index.html',
            url=url,
        ), 422

    url = urlparse(url)
    url = f'{url.scheme}://{url.hostname}'

    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM urls WHERE name='{url}'")
        if not cur.fetchall():
            query = f"INSERT INTO urls (name, created_at) VALUES ('{url}', '{date.today()}')"
            cur.execute(query)
            conn.commit()
        else:
            cur.execute(f"SELECT * FROM urls WHERE name='{url}'")
            flash('Страница уже существует')
            return redirect(url_for('url_id', id=cur.fetchone()[0]))

        cur.execute(f"SELECT * FROM urls WHERE name='{url}'")
        flash('Страница успешно добавлена')
        return redirect(url_for('url_id', id=cur.fetchone()[0]))

@app.route('/urls/<int:id>')
def url_id(id):
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM urls WHERE id={id}")
        result = cur.fetchone()

    return render_template(
        'show.html',
        id=result[0],
        name=result[1],
        created_at=result[2],
    )

@app.get('/urls')
def get_urls():
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM urls")
        urls = cur.fetchall()[::-1]

    return render_template(
        'urls.html',
        urls=urls,
    )

def validate(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        return 'Некорректный URL'
    if len(url) > 255:
        return 'URL превышает 255 символов'

if __name__ == "__main__":
    app.run()
