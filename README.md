# Cinemas Site

This script get info from [afisha.ru](https://www.afisha.ru/msk/schedule_cinema/) and [kinopoisk.ru](https://www.kinopoisk.ru/) and build site with it.\
Info on site:
- Movie poster.
- Movie title and page on [afisha.ru](https://www.afisha.ru).
- Movie genres.
- Movie plot.
- Rating by [kinopoisk.ru](https://www.kinopoisk.ru/)
- Cinema counts, which now shows movie

There is also a API, which returns information in JSON format.\
Working example on [heroku](https://peaceful-oasis-41133.herokuapp.com/).
# How to install
1. Recomended use venv or virtualenv for better isolation.\
Venv setup example: \
`$python3 -m venv myenv`\
`source myenv/bin/activate`
2. Install requirements:\
`$pip3 install -r requirements.txt` (alternatively try add `sudo` before command)\

# How to launch
   - Go to `25_cinemas_count` folder.
   - Run server `gunicorn server:app -t 300`
   - Open on browser `http://127.0.0.1:8000`
   - For API page: `http://127.0.0.1:8000/api_movie`
# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
