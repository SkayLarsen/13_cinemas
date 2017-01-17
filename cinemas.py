import requests
import random
from bs4 import BeautifulSoup


def fetch_afisha_page():
    url = 'http://www.afisha.ru/msk/schedule_cinema/'
    return requests.get(url).text


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    movies = soup.find_all('div', 'm-disp-table')
    return [{
                'title': movie.find('a').text,
                'cinemas': len(movie.parent.find_all('td', 'b-td-item'))}
            for movie in movies]


def fetch_movie_info(movie_title):
    timeout = 10
    url = 'https://www.kinopoisk.ru/index.php?first=yes&what=&kp_query='
    try:
        return requests.get(''.join([url, movie_title]),
                            proxies={"http": random.choice(proxy_list)}, timeout=timeout).content
    except (requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ProxyError,
            requests.exceptions.ReadTimeout):
        return None


def parse_kinopoisk_page(page):
    try:
        soup = BeautifulSoup(page, 'html.parser')
        return {
            'ball': soup.find('span', 'rating_ball').text,
            'count': soup.find('span', 'ratingCount').text
        }
    except (AttributeError, TypeError, ValueError):
        return None


def make_movies_list(movies, minimal_popularity=10):
    movies = filter(lambda movie: movie['cinemas'] >= minimal_popularity, movies)
    movies_list = []
    for movie in movies:
        info = fetch_movie_info(movie['title'])
        rating = parse_kinopoisk_page(info)
        if rating is None:
            rating = {'ball': 0, 'count': 0}
        movies_list.append((movie['title'], rating['ball'], rating['count'], movie['cinemas']))
    return movies_list


def output_movies_to_console(movies_list, top_count=10):
    for movie, rating_ball, rating_count, cinemas in \
            sorted(movies_list, key=lambda rate: float(rate[1]), reverse=True)[:top_count]:
        print('Фильм "{}" имеет среднюю оценку {} на основании {} голосов и идёт в {} кинотеатрах'.format(
            movie, rating_ball, rating_count, cinemas
        ))


if __name__ == '__main__':
    proxy_url = "http://www.freeproxy-list.ru/api/proxy"
    proxy_params = {'anonymity': 'true', 'token': 'demo'}
    proxy_list = requests.get(proxy_url, params=proxy_params).text.split('\n')
    movies = parse_afisha_list(fetch_afisha_page())
    movies_list = make_movies_list(movies)
    output_movies_to_console(movies_list)
