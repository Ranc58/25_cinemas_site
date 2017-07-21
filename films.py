import requests
from multiprocessing import Pool
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
        if cinemas_count > 30 and film_name.text != 'Овердрайв':  # TODO del film_name.text
            film_info_dict = {'name': film_name.text,
                              'cinemas_count': cinemas_count,
                              'afisha_film_url': film_url}
            cinemas_count_list.append(film_info_dict)
    return cinemas_count_list


def get_kinopoisk_films_id(movie):
    movies = Movie.objects.search(movie['name'])
    movie_from_afisha = movies[0]
    movie_from_afisha.get_content('main_page')
    movie_from_afisha.get_content('posters')
    movie_id_name_plot_poster = {'id': movie_from_afisha.id,
                                 'name': movie_from_afisha.title,
                                 'description': movie_from_afisha.plot,
                                 'poster': movie_from_afisha.posters[0]}
    return movie_id_name_plot_poster


def get_xml_kinopoisk_list(movie):
    context = requests.get(KINOPOISK_XML.
                           format(movie['id']))
    return context


def parse_rate_kinopoisk(movie):
    moive_rate = bs(movie.text, 'lxml')
    rate = moive_rate.find('kp_rating')
    counts_rate = moive_rate.find('kp_rating')['num_vote']
    rating_dict = {'rate': float(rate.text),
                   'counts_rate': counts_rate}
    return rating_dict


def get_output_fimls(movies_info, kinopoisk_rates, cinemas_count_list):
    rate_counts_min = 300
    movies_info_list = [dict(x, **y)
                        for x, y in zip(movies_info, kinopoisk_rates)]
    for movies, cinemas in zip(movies_info_list, cinemas_count_list):
        movies['cinemas_count'] = cinemas['cinemas_count']
    movies_info_list = [x for x in movies_info_list
                        if int(x.get('counts_rate')) > rate_counts_min]
    movies_info_list = sorted(movies_info_list,
                              key=itemgetter('rate'), reverse=True)
    return movies_info_list


def parse_films():
    pool=ThreadPool(4)
    afisha_raw_html = fetch_afisha_page(URL_AFISHA)
    cinemas_count_list = parse_afisha_list(afisha_raw_html)
    movies_info = pool.map(get_kinopoisk_films_id, cinemas_count_list)
    xml_kinopoisk_list = pool.map(get_xml_kinopoisk_list, movies_info)
    kinopoisk_rates = pool.map(parse_rate_kinopoisk, xml_kinopoisk_list)
    pool.close()
    pool.join()
    return get_output_fimls(movies_info, kinopoisk_rates, cinemas_count_list)
