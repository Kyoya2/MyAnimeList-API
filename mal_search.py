import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from mal_common import EntryContainer

ANIME_SEARCH_URL = r'https://myanimelist.net/anime.php?cat=anime&c[]=a&c[]=b&c[]=c&c[]=d&c[]=e&c[]=f&c[]=g'

link_to_id = lambda link: int(re.search(r'/anime/(\d+)/', link)[1])
str_to_int = lambda s: int(s.replace(',', ''))

def search_anime(query):
    response_html = requests.get(ANIME_SEARCH_URL, params={'q':query}).content.decode()
    soup = BeautifulSoup(response_html, features='lxml')
    data = soup.select('.js-categories-seasonal > table:nth-child(1) > tr')[1:] # Skip first row (header row)

    results = []
    for search_result in data:
        # Parse title and id
        title_data = search_result.select('td:nth-child(2) > div:nth-child(1) > a:nth-child(2)')[0]
        title = title_data.strong.contents[0]
        anime_id = link_to_id(title_data['href'])

        # Parse additional info
        additional_info = list(c for c in search_result.children if c != '\n')[2:]
        anime_type, num_episodes, score, start_date, end_date, num_users, rating = [e.contents[0].strip() for e in additional_info]

        num_episodes = 0 if num_episodes=='-' else str_to_int(num_episodes)
        score = 0 if score=='N/A' else float(score)
        num_users = str_to_int(num_users)
        
        results.append(EntryContainer({
            'title': title,
            'id': anime_id,
            'type': anime_type,
            'num_episodes': num_episodes,
            'score': score,
            'start_date': start_date,
            'end_date': end_date,
            'num_users': num_users,
            'rating': rating}))
    
    return results


if __name__ == '__main__':
    print(search_anime('texhnolyze')[0])