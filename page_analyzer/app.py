from flask import Flask, render_template, request, flash, redirect, url_for
import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv, find_dotenv
from datetime import date
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


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
    url = f'{url.scheme}://{url.netlock}'

    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute(sql.SQL('SELECT * FROM {} WHERE {}=%s')
                    .format(sql.Identifier('urls'), sql.Identifier('name')),
                    [url])
        if cur.fetchone():
            cur.execute(sql.SQL('SELECT * FROM {} WHERE {}=%s')
                        .format(sql.Identifier('urls'), sql.Identifier('name')),
                        [url])
            flash('Страница уже существует')
            return redirect(url_for('url_id', id=cur.fetchone()[0]))
        else:
            cur.execute(sql.SQL("INSERT INTO {} ({}, {}) VALUES (%s, %s)")
                        .format(sql.Identifier('urls'), sql.Identifier('name'),
                                sql.Identifier('created_at')),
                        [url, date.today()])
            conn.commit()
        cur.execute(sql.SQL('SELECT * FROM {} WHERE {}=%s')
                    .format(sql.Identifier('urls'), sql.Identifier('name')),
                    [url])
        flash('Страница успешно добавлена')
        return redirect(url_for('url_id', id=cur.fetchone()[0]))


@app.route('/urls/<int:id>')
def url_id(id):
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor() as cur:
        cur.execute(sql.SQL('SELECT * FROM {} WHERE {}=%s')
                    .format(sql.Identifier('urls'), sql.Identifier('id')),
                    [id])
        url = cur.fetchone()
        cur.execute(sql.SQL('SELECT * FROM {} WHERE {}=%s')
                    .format(sql.Identifier('url_checks'),
                            sql.Identifier('url_id')),
                    [id])
        check = cur.fetchall()[::-1]

    return render_template(
        'show.html',
        id=url[0],
        name=url[1],
        created_at=url[2],
        check=check,
    )


@app.get('/urls')
def get_urls():
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM urls")
        cur.execute(sql.SQL('SELECT * FROM {}')
                    .format(sql.Identifier('urls')))
        urls = cur.fetchall()[::-1]
        query = 'SELECT url_id,' \
                ' MAX(b.status_code),' \
                ' MAX(b.created_at) AS last_tested_at' \
                ' FROM urls a' \
                ' INNER JOIN url_checks b ON a.id = b.url_id' \
                ' GROUP BY url_id' \
                ' ORDER BY url_id;'
        cur.execute(query)
        result = cur.fetchall()

    checks = {}
    for item in result:
        checks[item[0]] = [item[1], item[2]]
    for item in urls:
        if item[0] not in checks:
            checks[item[0]] = ['', '']

    return render_template(
        'urls.html',
        urls=urls,
        checks=checks,
    )


@app.post('/urls/<int:id>/checks')
def check_url(id):
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor() as cur:
        cur.execute(sql.SQL('SELECT * FROM {} WHERE {}=%s')
                    .format(sql.Identifier('urls'), sql.Identifier('id')),
                    [id])
        url = cur.fetchone()

        try:
            r = requests.get(url[1])
        except requests.exceptions.RequestException:
            flash('Произошла ошибка при проверке', 'warning')
            return redirect(url_for('url_id', id=url[0]))
        soup = BeautifulSoup(r.text, 'lxml')
        h1 = soup.find('h1')
        title = soup.find('title')
        meta_tag = soup.find('meta', {'name': 'description'})
        if h1:
            h1 = h1.text
        else:
            h1 = ''
        if title:
            title = title.text
        else:
            title = ''
        if meta_tag:
            content = meta_tag['content']
        else:
            content = ''
        cur.execute(sql.SQL('INSERT INTO {} ({}, {}, {}, {}, {}, {})'
                            'VALUES (%s, %s, %s, %s, %s, %s)')
                    .format(sql.Identifier('url_checks'),
                            sql.Identifier('url_id'),
                            sql.Identifier('status_code'),
                            sql.Identifier('h1'),
                            sql.Identifier('title'),
                            sql.Identifier('description'),
                            sql.Identifier('created_at')),
                    [url[0], r.status_code, h1,
                     title, content,
                     date.today()])
        conn.commit()

    flash('Страница успешно проверена')
    return redirect(url_for('url_id', id=url[0]))


def validate(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        return 'Некорректный URL'
    if len(url) > 255:
        return 'URL превышает 255 символов'


if __name__ == "__main__":
    app.run()
