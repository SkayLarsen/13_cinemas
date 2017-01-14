import requests
import random
from bs4 import BeautifulSoup


def fetch_afisha_page():
    url = 'http://www.afisha.ru/msk/schedule_cinema/'
    return requests.get(url).text


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    movies = soup.find_all('div', 'm-disp-table')
    return [
        (movie.find('a').text,  # название
         len(movie.parent.find_all('td', 'b-td-item')))  # количество кинотеатров
        for movie in movies]


def fetch_movie_info(movie_title):
    timeout = 10
    url = 'https://www.kinopoisk.ru/index.php?first=yes&what=&kp_query='
    try:
        movie_page = requests.get(''.join([url, movie_title]),
                                  proxies={"http": random.choice(proxy_list)}, timeout=timeout).content
    except requests.exceptions.ConnectionError:
        return None, None
    soup = BeautifulSoup(movie_page, 'html.parser')
    rating_ball = soup.find('span', 'rating_ball').text
    rating_count = soup.find('span', 'ratingCount').text
    return rating_ball, rating_count


def make_movies_list(movies, cinema_count=10):
    movies = filter(lambda movie: movie[1] >= cinema_count, movies)
    movies_list = []
    for movie, cinemas in movies:
        rating_ball, rating_count = fetch_movie_info(movie)
        if rating_ball is None or rating_count is None:
            rating_ball, rating_count = 0, 0
        movies_list.append((movie, rating_ball, rating_count, cinemas))
    return movies_list


def output_movies_to_console(movies_list, top_count=10):
    for movie, rating_ball, rating_count, cinemas in \
            sorted(movies_list, key=lambda rate: float(rate[1]), reverse=True)[:top_count]:
        print('Фильм "{}" имеет среднюю оценку {} на основании {} голосов и идёт в {} кинотеатрах'.format(
            movie, rating_ball, rating_count, cinemas
        ))


if __name__ == '__main__':
    proxy_list = requests.get("http://www.freeproxy-list.ru/api/proxy",
                              params={'anonymity': 'true', 'token': 'demo'}).text.split('\n')
    movies = parse_afisha_list(fetch_afisha_page())
    movies_list = make_movies_list(movies)
    output_movies_to_console(movies_list)
