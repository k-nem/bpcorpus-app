import sqlite3
from flask import Flask, render_template, request, jsonify
from flask import g
from flask import Response
import json
import sys
from os import path

ROOT = path.dirname(path.realpath(__file__))

db = 'bpc.sqlite3'
app = Flask(__name__)

def execSql(db, query, var):
    con = sqlite3.connect(path.join(ROOT, db))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    if var:
        cur.execute(query, (var ,))
    else:
        cur.execute(query)
    rows = cur.fetchall()
    con.commit()
    con.close()

    return rows

def connect(db):
    con = sqlite3.connect(path.join(ROOT, db))
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    return cur

@app.route ('/')
def home():
    return render_template('home.html')

@app.route ('/authors')
def authors():
    query = 'select * from authors where work_count > 0 order by surname, name'
    rows = execSql(db, query, '')
    return render_template('authors.html', output = {'authors': rows})

@app.route ('/author/<id>', methods=['GET', 'POST'])
def author(id):

    tq = 'select * from text_meta where author_id = (?)'
    rows = execSql(db, tq, id)
    if rows:
        aid = rows[0]['author_id']
        an = rows[0]['author_name']

        return render_template('author.html', output = {'id': aid, 'name': an, 'texts': rows})

    else:
        return render_template('404.html'), 404

@app.route ('/text/<id>', methods=['GET', 'POST'])
def text(id):

    tiq = 'select * from text_meta where id = (?)'
    meta = execSql(db, tiq, id)

    txq = 'select html from text_files where id = (?)'
    txt = execSql(db, txq, id)[0][0]

    if meta:
        return render_template('text.html', output = {'meta': meta[0], 'txt': txt})

    else:
        return render_template('404.html'), 404

@app.route ('/search')
def search():
    return render_template('search.html', new = True)

@app.route ('/search', methods=['GET', 'POST'])
def search_post():
    query = request.form['wsearch']

    if len(query.split()) == 1:
        sq = 'select id, author_name, title from text_meta where id in (select id from search where wordlist MATCH (?))'
        results = execSql(db, sq, query)
        num = int(str(len(results))[-1]) #used purely for interface prompts

        return render_template('search.html', output = results, query = query, num = num)

    elif not query:
        return render_template('search.html', new = True)

    else:
        return render_template('search.html', resp = 'Некарэктны запыт. Запыт можа складацца толькі з аднаго слова.')

@app.route('/text/<id>/xml')
def xml_download(id):
    def generate(id):
        query = 'select xml from text_files where id = (?)'
        rows = execSql(db, query, id)
        return rows[0]
    return app.response_class(generate(id), mimetype='text/xml')

@app.route('/text/<id>/txt')
def text_download(id):
    def generate(id):
        query = 'select txt from text_files where id = (?)'
        rows = execSql(db, query, id)
        return rows[0]
    return app.response_class(generate(id), mimetype='text/plain')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host = '127.0.0.1', port = 5000, debug = True)
    authors()
