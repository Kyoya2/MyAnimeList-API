import requests
from bs4 import BeautifulSoup
import json
from mal_common import *
from datetime import datetime

# Get a list of 'AnimeListEntry' according to the list type
# see AnimeListType for possible 'list_type' values
def get_user_anime_list(mal_user_name: str, list_type: int) -> list:
    # Get HTML data of the anime list page
    response_html = requests.get(
        MAL_ALL_ANIME_LIST_LINK.format(
            user_name = mal_user_name,
            list_status = list_type)
        ).content.decode("utf-8")
    
    # Parse html and extract table data
    soup = BeautifulSoup(response_html, features='lxml')
    json_data = json.loads(soup.select('#list-container > div.list-block > div > table')[0]['data-items'])
    
    # Convert each entry to 'AnimeListEntry' and add it to the result list
    result = []
    for i, json_entry in enumerate(json_data):
        result.append(AnimeListEntry(
            status               = json_entry['status'],
            score                = json_entry['score'],
            user_tags            = str(json_entry['tags']).split(', '),
            is_rewatching        = json_entry['is_rewatching'] == IS_REWATCHING,
            num_watched_episodes = json_entry['num_watched_episodes'],
            num_episodes         = json_entry['anime_num_episodes'],
            title                = str(json_entry['anime_title']),
            id                   = json_entry['anime_id'],
            air_date             = json_entry['anime_start_date_string'],
            url                  = json_entry['anime_url']
        ))
    
    return result


def get_anime_character_list(anime_url: str):
    """
    Return (request_sent: bool, character_list: list)
    request_sent is True when a request is sent to myanimelist.com
    and False when the cache was used.
    """
    result = __get_characters_list_from_cache(anime_url)
    if result:
        # Make sure that the cache isn't empty or expired
        if (datetime.today() - datetime.strptime(result[0], CACHE_TIME_FORMAT)).days <= CACHE_LIFETIME_IN_DAYS:
            return (False, result[1])

    # Get HTML data of the characters list page
    response_html = requests.get(MAL_BASE_URL + anime_url + '/characters').content.decode("utf-8")
    soup = BeautifulSoup(response_html, features='lxml')

    # If the page doesn't containg the expected content, assume that the IP was suspended
    if len(soup.select('table > tr > td > div')) == 0:
        return (True, None)
    
    # Create a list that contains HTML data about each characterentries 
    characters_data = soup.select('table > tr > td > div > table > tr')
    
    result = []
    for character_row in characters_data:
        # The CSS Selector for the character list will also select the staff because
        # they appear in the same format at the bottom, so if we see that a 'character'
        # has no voice actors panel, it means that we reached the staff and we need to stop.
        voice_actors_container_data = character_row.select('td:nth-of-type(3) > table')
        
        if len(voice_actors_container_data) == 0:
            break
        
        # Extract voice actors data
        voice_actors = voice_actors_container_data[0].select('tr > td:nth-of-type(1)')
        character_voice_actors = []
        
        # Parse each voice actor for this character
        for voice_actor in voice_actors:
            character_voice_actors.append({
                'name'     : voice_actor.a.contents[0],
                'language' : voice_actor.small.contents[0],
                'id': __get_person_id_from_url(voice_actor.a['href'])
            })

        # Parse character data
        character_data = character_row.select('td:nth-of-type(2)')[0]
        
        character_is_main_role = character_data.div.small.contents[0].lower() == 'main'
        character_name = character_data.a.contents[0]
        character_link = character_data.a['href']
        character_id = __get_character_id_from_url(character_link)

        # Get the link to the image with the highest quality
        character_image_links = character_row.select('td:nth-of-type(1) > div > a > img')[0]['data-srcset'].split(', ')
        larges_character_image_link = max(character_image_links, key=(lambda item : item.split(' ')[1])).split(' ')[0]

        # Some MAL pages may not display the voice actors of a character, if that's the case then
        # we need to explicitly get the voice actors from that characters' page
        if len(character_voice_actors) == 0:
            character_voice_actors = get_character_voice_actors(character_id)
        
        result.append({
            'name'              : character_name,
            'is_main_character' : character_is_main_role,
            'id'                : character_id,
            'image_link'        : larges_character_image_link,
            'voice_actors'      : character_voice_actors
        })

    __write_characters_list_to_cache(result, anime_url)
    
    return (True, result)


def get_character_voice_actors(character_id) -> list:
    response_html = requests.get(MAL_CHARACTER_URL_PREFIX + str(character_id)).content.decode("utf-8")
    soup = BeautifulSoup(response_html, features='lxml')

    voice_actors = []
    
    voice_actors_data = soup.select('#content > table:nth-of-type(1) > tr:nth-of-type(1) > td:nth-of-type(2) > table > tr > td:nth-of-type(2)')
    
    for voice_actor_data in voice_actors_data:
        voice_actors.append({
            'name'     : voice_actor_data.a.contents[0],
            'language' : voice_actor_data.div.small.contents[0],
            'id'       : __get_person_id_from_url(voice_actor_data.a['href'])
        })
    
    return voice_actors


def __get_anime_id_from_url(anime_url: str) -> str:
    parts = anime_url.split('/')
    return parts[parts.index('anime') + 1]


def __get_character_id_from_url(character_url: str) -> str:
    parts = character_url.split('/')
    return parts[parts.index('character') + 1]


def __get_person_id_from_url(person_url: str) -> str:
    parts = person_url.split('/')
    return parts[parts.index('people') + 1]


def __get_characters_list_from_cache(anime_url: str) -> list:
    try:
        with open('.\\cache\\' + __get_anime_id_from_url(anime_url), 'r') as cache_file:
            return json.load(cache_file)
    except FileNotFoundError:
        return None


def __write_characters_list_to_cache(characters_list: list, anime_url: str):
    with open('.\\cache\\' + __get_anime_id_from_url(anime_url), 'w') as cache_file:
        return json.dump((datetime.today().strftime(CACHE_TIME_FORMAT), characters_list), cache_file)


def main():
    #/anime/31964/Boku_no_Hero_Academia
    #for e in (get_user_anime_list('Kyoya2', AnimeListType.AllAnime)):
    #    print(e)
    
    for e in get_anime_character_list('/anime/37515/Made_in_Abyss_Movie_2__Hourou_Suru_Tasogare'):
        print(repr(e) + '\n')


if __name__ == '__main__':
    main()