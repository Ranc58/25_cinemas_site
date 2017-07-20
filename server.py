from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from flask import Flask, render_template
from films import parse_films


app = Flask(__name__)

@app.route('/')
def films_list():
    return render_template('films_list.html', films=parse_films())

if __name__ == "__main__":
    app.run()
