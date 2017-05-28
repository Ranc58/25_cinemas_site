from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from flask import Flask, render_template
from flask.ext.cache import Cache
from films import parse_films

cache = Cache(config={'CACHE_TYPE':'simple'})

app = Flask(__name__)
cache.init_app(app)


@app.route('/')
@cache.cached(timeout=50)
def films_list():
    return render_template('films_list.html', films=parse_films())

if __name__ == "__main__":
    app.run()
