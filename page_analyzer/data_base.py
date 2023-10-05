import psycopg2
from psycopg2 import sql
from datetime import date


def get_connection(database):
    connection = psycopg2.connect(database)
    return connection


def add_url(connection, url):
    with connection.cursor() as cur:
        cur.execute(sql.SQL("INSERT INTO {} ({}, {}) VALUES (%s, %s)")
                    .format(sql.Identifier('urls'), sql.Identifier('name'),
                            sql.Identifier('created_at')),
                    [url, date.today()])
        connection.commit()


def get_url_by_name(connection, name):
    with connection.cursor() as cur:
        cur.execute(sql.SQL('SELECT * FROM {} WHERE {}=%s')
                    .format(sql.Identifier('urls'), sql.Identifier('name')),
                    [name])
        url = cur.fetchone()
        return url


def get_url_by_id(connection, id):
    with connection.cursor() as cur:
        cur.execute(sql.SQL('SELECT * FROM {} WHERE {}=%s')
                    .format(sql.Identifier('urls'), sql.Identifier('id')),
                    [id])
        url = cur.fetchone()
        return url


def get_url_checks(connection, id):
    with connection.cursor() as cur:
        cur.execute(sql.SQL('SELECT * FROM {} WHERE {}=%s')
                    .format(sql.Identifier('url_checks'),
                            sql.Identifier('url_id')),
                    [id])
        check = cur.fetchall()[::-1]
        return check


def get_urls(connection):
    with connection.cursor() as cur:
        cur.execute(sql.SQL('SELECT * FROM {}')
                    .format(sql.Identifier('urls')))
        urls = cur.fetchall()[::-1]
        return urls


def get_last_test(connection):
    with connection.cursor() as cur:
        query = 'SELECT url_id,' \
                ' MAX(b.status_code),' \
                ' MAX(b.created_at) AS last_tested_at' \
                ' FROM urls a' \
                ' INNER JOIN url_checks b ON a.id = b.url_id' \
                ' GROUP BY url_id' \
                ' ORDER BY url_id;'
        cur.execute(query)
        result = cur.fetchall()
        return result


def add_check(connection, *args):
    with connection.cursor() as cur:
        cur.execute(sql.SQL('INSERT INTO {} ({}, {}, {}, {}, {}, {})'
                            'VALUES (%s, %s, %s, %s, %s, %s)')
                    .format(sql.Identifier('url_checks'),
                            sql.Identifier('url_id'),
                            sql.Identifier('status_code'),
                            sql.Identifier('h1'),
                            sql.Identifier('title'),
                            sql.Identifier('description'),
                            sql.Identifier('created_at')),
                    [*args])
        connection.commit()
