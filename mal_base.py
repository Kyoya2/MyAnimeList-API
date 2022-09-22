import re
import json
import requests
from bs4 import BeautifulSoup
from mal_common import *
from time import ctime
from datetime import datetime, timedelta
from os.path import dirname, join


CACHE_DIRECTORY = join(dirname(__file__), 'cache')


# Get a list of entries according to the list type
# see AnimeListType for possible 'list_type' values
def get_user_anime_list(mal_user_name: str, list_type: int, main_sort_order=None, secondary_sort_order=None) -> list:
    # Generate MAL link from args
    anime_list_link = MAL_BASE_URL + f'/animelist/{mal_user_name}?status={list_type}'
    if main_sort_order is not None:
        anime_list_link += f'&order={main_sort_order}'
    if secondary_sort_order is not None:
        anime_list_link += f'&order2={secondary_sort_order}'

    # Get HTML data of the anime list page
    response_html = requests.get(anime_list_link).content.decode()
    
    # Parse html and extract table data
    soup = BeautifulSoup(response_html, features='lxml')
    json_data = json.loads(soup.select('#list-container > div.list-block > div > table')[0]['data-items'])
    
    # Reinterpret some fields as pythonic types for easier use
    result = []
    for json_entry in json_data:
        # Date fields
        for field_name in ('anime_start_date_string', 'anime_end_date_string'):
            if json_entry[field_name] is not None:
                json_entry[field_name] = datetime.strptime(json_entry[field_name], AIR_DATE_FORMAT)
        
        # Named entry lists
        for field_name in ('genres', 'demographics'):
            json_entry[field_name] = [entry['name'] for entry in json_entry[field_name]]
        
        # ctime entries
        for field_name in ('created_at', 'updated_at'):
            json_entry[field_name] = datetime.strptime(ctime(json_entry[field_name]), '%c')
        
        # Misc
        json_entry['tags'] = json_entry['tags'].split(', ')
        json_entry['is_rewatching'] = bool(json_entry['is_rewatching'])
            
        result.append(EntryContainer(json_entry))

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
            result  = [EntryContainer(entry) for entry in result[1]]
            for entry in result:
                entry.voice_actors = [EntryContainer(va) for va in entry.voice_actors]
            return (False, result)

    # Get HTML data of the characters list page
    response_html = requests.get(MAL_BASE_URL + anime_url + '/characters').content.decode()
    soup = BeautifulSoup(response_html, features='lxml')

    # If the page doesn't containg the expected content, assume that the IP was suspended
    character_container = soup.select('body > div#myanimelist > div.wrapper > div#contentWrapper > div#content > table > tr > td:nth-of-type(2)')
    if len(character_container) == 0:
        return (True, None)
    
    # Create a list that contains HTML data about each character
    characters_data = character_container[0].select('div.js-scrollfix-bottom-rel > div.anime-character-container > table.js-anime-character-table > tr')

    result = []
    for character_row in characters_data:
        # The CSS Selector for the character list will also select the staff because
        # they appear in the same format at the bottom, so if we see that a 'character'
        # has no voice actors panel, it means that we reached the staff and we need to stop.
        voice_actors_data = character_row.select('td:nth-of-type(3) > table > tr > td:nth-of-type(1)')
        
        character_voice_actors = []
        if len(voice_actors_data) > 0:
            # Parse each voice actor for this character
            for voice_actor in voice_actors_data:
                name, language = voice_actor.select('div')
                character_voice_actors.append(EntryContainer({
                    'name'     : name.a.contents[0].strip(),
                    'language' : language.contents[0].strip(),
                    'id': __get_person_id_from_url(name.a['href'].strip())
                }))

        # Parse character data
        character_data = character_row.select('td:nth-of-type(2)')[0]
        
        character_role, character_name = character_data.select('div.js-chara-roll-and-name')[0].contents[0].strip().split('_', 1)
        if character_role not in ('m', 's'):
            raise Exception(f'Unrecognized character role "{character_role}"')

        character_is_main_role = character_role == 'm'
        character_name = character_name
        character_link = character_data.select('div:nth-of-type(3)')[0].a['href'].strip()
        character_id = __get_character_id_from_url(character_link)

        # Get the link to the image with the highest quality
        character_image_links = character_row.select('td:nth-of-type(1) > div > a > img')[0]['data-srcset'].split(', ')
        larges_character_image_link = max(character_image_links, key=(lambda item : item.split(' ')[1])).split(' ')[0]

        # Some MAL pages may not display the voice actors of a character, if that's the case then
        # we need to explicitly get the voice actors from that characters' page
        if len(character_voice_actors) == 0:
            character_voice_actors = get_character_voice_actors(character_id)
        
        result.append(EntryContainer({
            'name'              : character_name,
            'is_main_character' : character_is_main_role,
            'id'                : character_id,
            'image_link'        : larges_character_image_link,
            'voice_actors'      : character_voice_actors
        }))

    __write_characters_list_to_cache(result, anime_url)
    
    return (True, result)


def get_character_voice_actors(character_id) -> list:
    response_html = requests.get(MAL_CHARACTER_URL_PREFIX + str(character_id)).content.decode()
    soup = BeautifulSoup(response_html, features='lxml')

    voice_actors = []
    
    voice_actors_data = soup.select('#content > table:nth-of-type(1) > tr:nth-of-type(1) > td:nth-of-type(2) > table > tr > td:nth-of-type(2)')
    
    for voice_actor_data in voice_actors_data:
        voice_actors.append(EntryContainer({
            'name'     : voice_actor_data.a.contents[0],
            'language' : voice_actor_data.div.small.contents[0],
            'id'       : __get_person_id_from_url(voice_actor_data.a['href'])
        }))
    
    return voice_actors


ANIME_DURATION_REGEX = re.compile('(?:(\d+) hr.)? ?(?:(\d+) min.)?')
def get_anime_duration(anime_id) -> timedelta:
    response_html = requests.get(MAL_ANIME_URL_PREFIX + str(anime_id)).content.decode()
    soup = BeautifulSoup(response_html, features='lxml')

    attributes = soup.select('div.spaceit_pad')
    for attr in attributes:
        if attr.span and attr.span.contents[0] == 'Duration:':
            duration_str = list(attr.children)[-1].strip()
    
    match = ANIME_DURATION_REGEX.search(duration_str)
    return timedelta(
        hours   = int(match[1] or 0),
        minutes = int(match[2] or 0)
    )


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
        with open(join(CACHE_DIRECTORY, __get_anime_id_from_url(anime_url) + '.json'), 'r', encoding='utf8') as cache_file:
            return json.load(cache_file)
    except FileNotFoundError:
        return None


def __write_characters_list_to_cache(characters_list: list, anime_url: str):
    with open(join(CACHE_DIRECTORY, __get_anime_id_from_url(anime_url) + '.json'), 'w', encoding='utf8') as cache_file:

        serializable_list = [entry._dict for entry in characters_list]
        for entry in serializable_list:
            entry['voice_actors'] = [va._dict for va in entry['voice_actors']]

        json.dump((datetime.today().strftime(CACHE_TIME_FORMAT), serializable_list), cache_file)


def main():
    print(get_anime_duration(3785))
    
    #for e in get_anime_character_list('/anime/37515/Made_in_Abyss_Movie_2__Hourou_Suru_Tasogare'):
    #    print(e.title_localized)


if __name__ == '__main__':
    main()