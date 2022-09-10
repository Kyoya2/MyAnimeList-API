from collections import namedtuple

# Constants
MAL_BASE_URL = 'https://myanimelist.net'
MAL_ALL_ANIME_LIST_LINK = MAL_BASE_URL + '/animelist/{user_name}?status={list_status}&order=-14'
MAL_CHARACTER_URL_PREFIX = 'https://myanimelist.net/character/'
CACHE_LIFETIME_IN_DAYS = 100
CACHE_TIME_FORMAT = '%d/%m/%Y'
AIR_DATE_FORMAT = '%d-%m-%y'


class AnimeStatus:
    Watching    = 1
    Completed   = 2
    OnHold      = 3
    Dropped     = 4
    PlanToWatch = 6

class AnimeListType:
    Watching    = 1
    Completed   = 2
    OnHold      = 3
    Dropped     = 4
    PlanToWatch = 6
    AllAnime    = 7

class AnimeAiringStatus:
    Airing          = 1
    FinishedAiring  = 2
    NotAiredYet     = 3

# Negate the value to get a reversed order
class AnimeListSortBy:
    AnimeTitle      = 1
    FinishDate      = 2
    StartDate       = 3
    Score           = 4
    LastUpdated     = 5
    Type            = 6
    Rating          = 8
    RewatchValue    = 9
    Priority        = 11
    WatchedEpisodes = 12
    Storage         = 13
    AirStartDate    = 14
    AirEndDate      = 15
    Status          = 16

class CharacterRole:
    Main        = 0
    Supporting  = 1