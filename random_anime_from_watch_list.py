import my_anime_list
from mal_common import AnimeListType, MAL_BASE_URL
import random
from os import system


def main():
    mal_username = 'Kyoya2'#input('Enter your MAL username: ')
    plan_to_watch = my_anime_list.get_user_anime_list(mal_username, AnimeListType.PlanToWatch)
    system(f'start "" {MAL_BASE_URL + random.choice(plan_to_watch).url}')


if __name__ == '__main__':
    main()