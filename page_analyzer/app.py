from flask import Flask, render_template, request, flash, redirect, url_for
import os
from dotenv import load_dotenv, find_dotenv
from datetime import date
from urllib.parse import urlparse
import requests
from page_analyzer import data_base
from page_analyzer.seo import get_seo
from page_analyzer.validator import validate, normalize_url


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
    data = request.form.to_dict()['url']

    if not data:
        flash('URL обязателен', 'warning')
        return render_template(
            'index.html',
        ), 422

    error = validate(data)

    if error:
        flash(error)
        return render_template(
            'index.html',
            url=data,
        ), 422

    url = normalize_url(urlparse(data))

    conn = data_base.get_connection(DATABASE_URL)

    db_url = data_base.get_url_by_name(conn, url)
    if db_url:
        flash('Страница уже существует')
        return redirect(url_for('url_id', id=db_url[0]))
    else:
        data_base.add_url(conn, url)
        db_url = data_base.get_url_by_name(conn, url)
        flash('Страница успешно добавлена')
        return redirect(url_for('url_id', id=db_url[0]))


@app.route('/urls/<int:id>')
def url_id(id):
    conn = data_base.get_connection(DATABASE_URL)

    url = data_base.get_url_by_id(conn, id)

    check = data_base.get_url_checks(conn, id)

    return render_template(
        'show.html',
        id=url[0],
        name=url[1],
        created_at=url[2],
        check=check,
    )


@app.get('/urls')
def get_urls():
    conn = data_base.get_connection(DATABASE_URL)

    urls = data_base.get_urls(conn)

    last_tests = data_base.get_last_test(conn)

    checks = {}
    for item in last_tests:
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
    conn = data_base.get_connection(DATABASE_URL)

    url = data_base.get_url_by_id(conn, id)

    try:
        r = requests.get(url[1])
        r.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_id', id=url[0]))

    h1, title, content = get_seo(r)

    data_base.add_check(conn,
                        url[0],
                        r.status_code,
                        h1,
                        title,
                        content,
                        date.today()
                        )

    flash('Страница успешно проверена')
    return redirect(url_for('url_id', id=url[0]))


if __name__ == "__main__":
    app.run()
