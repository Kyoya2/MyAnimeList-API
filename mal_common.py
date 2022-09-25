from contextlib import contextmanager
from datetime import datetime
from time import sleep

MAL_BASE_URL = 'https://myanimelist.net'
MAL_ANIME_URL_PREFIX = MAL_BASE_URL + '/anime/'
MAL_CHARACTER_URL_PREFIX = MAL_BASE_URL + '/character/'
CACHE_LIFETIME_IN_DAYS = 100
CACHE_TIME_FORMAT = '%d/%m/%Y'
AIR_DATE_FORMAT = '%d-%m-%y'
MAL_REQUEST_INTERVAL = 3 # seconds

__LAST_MAL_REQUEST_TIME = datetime.min


class EntryContainer(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def copy(self):
        return EntryContainer(super().copy())


@contextmanager
def mal_request():
    """
    This context manager makes sure that there are at least MAL_REQUEST_INTERVAL
    seconds between each request to avoid getting the IP suspended for request
    flooding. Each request to MyAnimeList website should be made in a different
    instance of this context manager.
    """
    global __LAST_MAL_REQUEST_TIME

    time_delta = datetime.now() - __LAST_MAL_REQUEST_TIME
    if time_delta.total_seconds() < MAL_REQUEST_INTERVAL:
        sleep(MAL_REQUEST_INTERVAL - time_delta.total_seconds())

    try:
        yield
    finally:
        __LAST_MAL_REQUEST_TIME = datetime.now()


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