import requests
from multiprocessing.dummy import Pool as ThreadPool
from operator import itemgetter
from bs4 import BeautifulSoup as bs
from kinopoisk.movie import Movie

URL_AFISHA = 'https://www.afisha.ru/msk/schedule_cinema/#'
KINOPOISK_XML = 'https://rating.kinopoisk.ru/{}.xml'


def fetch_afisha_page(URL_AFISH):
    afisha_raw_html = requests.get(URL_AFISHA).content
    return afisha_raw_html


def parse_afisha_list(afisha_raw_html):
    parse_info = bs(afisha_raw_html, "lxml")
    movie_list = parse_info.find('div',
                                 {'class':
                                  'b-theme-schedule m-schedule-with-collapse'})
    movies = movie_list.findAll('div',
                                {'class':
                                 'object s-votes-hover-area collapsed'})
    cinemas_count_list = []
    for item in movies:
        film_name = item.find('h3', {'class': 'usetags'})
        cinemas = item.findAll('td', {'class': 'b-td-item'}, 'a')
        cinemas_count = len(cinemas)
        film_url = item.h3.a['href']
        film_info_dict = {'name': film_name.text,
                          'cinemas_count': cinemas_count,
                          'afisha_film_url': str(film_url)}
        cinemas_count_list.append(film_info_dict)
    return cinemas_count_list


def filter_afisha_movies(all_cinemas_count_list):
    min_cinema_counts = 30
    cinemas_count_lists = [movie for movie in all_cinemas_count_list
                           if movie['cinemas_count'] > min_cinema_counts]
    return cinemas_count_lists


def fetch_afisha_film_page(movie):
    movie_content = requests.get(movie['afisha_film_url']).content
    return movie_content.decode('utf8')


def parse_afisha_film(movie_content):
    movie_info = bs(movie_content, "lxml")
    plot_tag = {'id':
                'ctl00_CenterPlaceHolder_ucMainPageContent_pEditorComments'}
    movie_plot = movie_info.find('p', plot_tag)
    genres = movie_info.findAll('div', {'class': 'b-tags'}, 'a')
    return {'description': movie_plot, 'genres': genres[0].text}


def get_full_afisha_info(cinemas_count_list, afisha_film_info):
    afisha_info_list = [dict(x, **y)
                        for x, y in zip(afisha_film_info, cinemas_count_list)]
    return afisha_info_list


def get_kinopoisk_films_id(movie):
    movies = Movie.objects.search(movie['name'])
    movie_from_afisha = movies[0]
    movie_from_afisha.get_content('posters')
    movie_id_name_plot_poster = {'id': movie_from_afisha.id,
                                 'name': movie_from_afisha.title,
                                 'poster': movie_from_afisha.posters[0]}
    return movie_id_name_plot_poster


def get_xml_kinopoisk_list(movie):
    content = requests.get(KINOPOISK_XML.
                           format(movie['id']))
    return content


def parse_rate_kinopoisk(xml_kinopoisk_list):
    rating_list = []
    for movie in xml_kinopoisk_list:
        moive_rate = bs(movie.text, 'lxml')
        rate = moive_rate.find('kp_rating')
        counts_rate = moive_rate.find('kp_rating')['num_vote']
        rating_dict = {'rate': float(rate.text),
                       'counts_rate': counts_rate}
        rating_list.append(rating_dict)
    return rating_list


def format_info_for_output(movies_info, kinopoisk_rates, afisha_info_list):
    rate_counts_min = 300
    movies_info_list = [dict(x, **y)
                        for x, y in zip(movies_info, kinopoisk_rates)]
    for movies, cinemas in zip(movies_info_list, afisha_info_list):
        movies['cinemas_count'] = cinemas['cinemas_count']
        movies['afisha_film_url'] = cinemas['afisha_film_url']
        if cinemas['description'] is None:
            cinemas['description'] = 'Нет информации'
        else:
            cinemas['description'] = cinemas['description'].text
        movies['description'] = cinemas['description'].strip()
        movies['genres'] = cinemas['genres'].strip()
    movies_info_list = [x for x in movies_info_list
                        if int(x.get('counts_rate')) > rate_counts_min]
    films_info_list = sorted(movies_info_list,
                             key=itemgetter('rate'), reverse=True)
    return films_info_list


def filter_output_films(films_info_list):
    top_10_movies = films_info_list[:10]
    return top_10_movies


def parse_films():
    threads_counts = 8
    pool = ThreadPool(threads_counts)
    afisha_raw_html = fetch_afisha_page(URL_AFISHA)
    all_cinemas_count_list = parse_afisha_list(afisha_raw_html)
    cinemas_count_list = filter_afisha_movies(all_cinemas_count_list)
    movie_content = pool.map(fetch_afisha_film_page, cinemas_count_list)
    afisha_film_info = pool.map(parse_afisha_film, movie_content)
    afisha_info_list = get_full_afisha_info(cinemas_count_list,
                                            afisha_film_info)
    movies_info = pool.map(get_kinopoisk_films_id, cinemas_count_list)
    xml_kinopoisk_list = pool.map(get_xml_kinopoisk_list, movies_info)
    kinopoisk_rates = parse_rate_kinopoisk(xml_kinopoisk_list)
    films_info_list = format_info_for_output(movies_info,
                                             kinopoisk_rates,
                                             afisha_info_list)
    top_10_movies = filter_output_films(films_info_list)
    return top_10_movies

if __name__ == "__main__":
    parse_films()
