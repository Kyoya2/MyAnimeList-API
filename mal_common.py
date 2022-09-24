MAL_BASE_URL = 'https://myanimelist.net'
MAL_ANIME_URL_PREFIX = MAL_BASE_URL + '/anime/'
MAL_CHARACTER_URL_PREFIX = MAL_BASE_URL + '/character/'
CACHE_LIFETIME_IN_DAYS = 100
CACHE_TIME_FORMAT = '%d/%m/%Y'
AIR_DATE_FORMAT = '%d-%m-%y'


class EntryContainer:
    def __init__(self, d):
        self._dict = d
        for k, v in d.items():
            setattr(self, k, v)

    def copy(self):
        return EntryContainer(self._dict.copy())

    def __repr__(self):
        return repr(self._dict)


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