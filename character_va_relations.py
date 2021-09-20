from my_anime_list import get_user_anime_list, get_anime_character_list
from mal_common import AnimeListType, AnimeStatus, MAL_CHARACTER_URL_PREFIX
from time import sleep
from collections import namedtuple
from functools import reduce
from os import system
from pprint import PrettyPrinter

ANIME_GET_INTRERVAL = 3 # The lower this is, the higher the chance that MAL will suspend your IP temporarily
RETRY_INTERVAL = 60 # The time (in seconds) to wait after MAL has suspended your IP
VOICE_ACTOR_LANGUAGE = 'Japanese'
CHARACTER_TYPE_SORT_ORDER = (AnimeStatus.Completed, AnimeStatus.Watching, AnimeStatus.OnHold, AnimeStatus.Dropped)

TABLE_CHARACTER_ROW_FORMAT = '<tr><td><table><tr>{character_name_cells}</tr><tr>{character_image_cells}</tr></table></td></tr>'
TABLE_CHARACTER_NAME_CELL_FORMAT = '<td><a href="{character_page_link}">{character_name}</a></td>'
TABLE_CHARACTER_IMAGE_CELL_FORMAT = '<td><img src={character_image_link} title="{character_image_alt_text}"/></td>'

AnimeCharacter = namedtuple('AnimeCharacter', ['name', 'is_main_character', 'id', 'character_image_link', 'anime_status'])

def format_html_string_width(string: str, line_length: int) -> str:
    words = string.split(' ')
    result = ''

    current_line_length = -1
    for word in words:
        if len(word) + 1 + current_line_length > line_length:
            result += "<br/>"
            current_line_length = 0

        result += word + ' '
        current_line_length += len(word) + 1
    
    return result[:-1]


def main():
    mal_username = input('Enter your MAL username: ')
    print('Getting anime list')
    user_anime_list = get_user_anime_list(mal_username, AnimeListType.AllAnime)

    # {'ID of voice actor': [all the characters he/she voices], ...}
    voice_actor_characters = dict()

    # {'ID of an anime character': [titles of animes that the character appears in], ...}
    character_anime_appearances = dict()

    print('Getting characters from all anime')
    for anime in user_anime_list:
        # Ignore anime that's marked as plan to watch
        if anime.status == AnimeStatus.PlanToWatch:
            continue

        print(anime.title)

        # Retry until successfully getting the character list of the current anime
        while True:
            request_sent, characters = get_anime_character_list(anime.url)
            if characters is not None:
                break
            else:
                sleep(RETRY_INTERVAL)

        for current_character in characters:
            if current_character['id'] not in character_anime_appearances:
                character_anime_appearances.update({current_character['id']: []})

            # Some characters may appear several times in different anime, insert them only once
            for voice_actor in current_character['voice_actors']:
                # Make sure to take characters only from the voice actor of the specified language
                if voice_actor['language'].lower() == VOICE_ACTOR_LANGUAGE.lower():
                    # Create the list for this voice actor if it doesn't exist
                    if voice_actor['id'] not in voice_actor_characters:
                        voice_actor_characters.update({voice_actor['id'] : []})

                    # Add this character only if it isn't already in the list (perhaps it was added from another anime)
                    if not any([(current_character['id'] == character.id) for character in voice_actor_characters[voice_actor['id']]]):
                        voice_actor_characters[voice_actor['id']].append(AnimeCharacter(
                            name = current_character['name'],
                            is_main_character = current_character['is_main_character'],
                            id = current_character['id'],
                            character_image_link = current_character['image_link'],
                            anime_status = anime.status
                        ))

            character_anime_appearances[current_character['id']].append(anime.title)

        if request_sent:
            sleep(ANIME_GET_INTRERVAL)
    
    # We don't care about the voice actors themselves so we make a list of lists:
    # [[characters voiced by voice actor 1], [characters voiced by voice actor 2], ...]
    rows_data = list(voice_actor_characters.values())
    del voice_actor_characters
    
    # Sorting each row by the following priorities
    # 1) Anime status priority order: Completed > Watching > On-hold > Dropped
    # 2) Is main character
    for characters in rows_data:
        characters.sort(key=(lambda item : item.is_main_character), reverse=True)
        characters.sort(key=(lambda item : CHARACTER_TYPE_SORT_ORDER.index(item.anime_status)))
    
    # Sorting all rows by the following priorities
    # 1) Number of characters
    # 2) Number of main characters
    rows_data.sort(key=(lambda item : reduce(lambda crnt_sum, crnt_item : crnt_sum + (1 if crnt_item.is_main_character else 0), item, 0)), reverse=True)
    rows_data.sort(key=(lambda item : len(item)), reverse=True)

    # Generating html table
    rows_iterator = iter(rows_data)
    html_rows = ''

    # Iterating over lists of characters with the same voice actor
    for current_row in rows_data:
        character_name_cells = ''
        character_image_cells = ''

        # Generating row content
        for character in current_row:
            character_name_cells += TABLE_CHARACTER_NAME_CELL_FORMAT.format(
                character_page_link = MAL_CHARACTER_URL_PREFIX + character.id,
                character_name = format_html_string_width(character.name, 10)
            )
            character_image_cells += TABLE_CHARACTER_IMAGE_CELL_FORMAT.format(
                character_image_link = character.character_image_link,
                character_image_alt_text = '\n'.join(character_anime_appearances[character.id])
            )

        # Formatting row
        html_rows += TABLE_CHARACTER_ROW_FORMAT.format(
            character_name_cells = character_name_cells,
            character_image_cells = character_image_cells
        )
            
    # Writing result to file
    with open('template.html', 'r') as template_file:
        html_template = template_file.read()
    
    with open(f'.\\user lists\\{mal_username}.html', 'w', encoding='utf8') as output_file:
        output_file.write(html_template.replace('{CONTENT_PLACEHOLDER}', html_rows))
    
    system(f'start "" ".\\user lists\\{mal_username}.html"')


if __name__ == '__main__':
    main()