from collections import namedtuple

# Constants
MAL_BASE_URL = 'https://myanimelist.net'
MAL_ALL_ANIME_LIST_LINK = MAL_BASE_URL + '/animelist/{user_name}?status={list_status}&order=-14'
MAL_CHARACTER_URL_PREFIX = 'https://myanimelist.net/character/'
IS_REWATCHING = 1
CACHE_LIFETIME_IN_DAYS = 100
CACHE_TIME_FORMAT = '%d/%m/%Y'

# Structs
AnimeListEntry = namedtuple('AnimeListEntry', ['title', 'id', 'status', 'score', 'user_tags', 'is_rewatching', 'num_episodes', 'num_watched_episodes', 'air_date', 'url'])
# AnimeCharacter = namedtuple('AnimeCharacter', ['name', 'is_main_character', 'url', 'image_link', 'voice_actors'])
# AnimeVoiceActor = namedtuple('AnimeVoiceActor', ['name', 'language', 'url'])

# Enums
class AnimeStatus():
    Watching    = 1
    Completed   = 2
    OnHold      = 3
    Dropped     = 4
    PlanToWatch = 6

class AnimeListType():
    Watching    = 1
    Completed   = 2
    OnHold      = 3
    Dropped     = 4
    PlanToWatch = 6
    AllAnime    = 7

class CharacterRole():
    Main        = 0
    Supporting  = 1