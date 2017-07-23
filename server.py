# -*- coding: utf-8 -*-
import json
import tempfile
from flask import Flask, render_template, Response
from werkzeug.contrib.cache import FileSystemCache
from movie_parser import parse_films


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
tmp_dir = tempfile.mkdtemp()
cache = FileSystemCache(cache_dir=tmp_dir)


def get_movies_from_cache():
    movies = cache.get('movies')
    if movies is None:
        movies = parse_films()
        cache.set('movies', movies, timeout=12 * 60 * 60)
    return movies


@app.route('/')
def films_list():
    return render_template('films_list.html', films=get_movies_from_cache())


@app.route('/api_movies')
def get_api():
    return Response(json.dumps(get_movies_from_cache(),
                               indent=2, ensure_ascii=False),
                    content_type='application/json; charset=utf-8')


if __name__ == "__main__":
    app.run()
