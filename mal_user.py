from mal_base import *
from os import path
import re
import json
import requests
import secrets


class MyAnimeListUser:
    def __init__(self, client_id, mal_tokens_file_path):
        self._client_id = client_id
        self._tokens_file_path = mal_tokens_file_path
        if not path.isfile(mal_tokens_file_path):
            self._generate_tokens()
        else:
            with open(self._tokens_file_path) as f:
                self._update_tokens(json.load(f), save_to_file=False)

    def get_user_info(self):
        return self._send_authenticated_request('GET', 'users/@me')

    def update_anime_episode_count(self, anime_id, new_episode_count):
        return self._send_authenticated_request(
            'PATCH',
            f'anime/{anime_id}/my_list_status',
            data=f'num_watched_episodes={new_episode_count}',
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

    def _generate_tokens(self):
        challenge = secrets.token_urlsafe(100)[:128]
        print('Go to', f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={self._client_id}&code_challenge={challenge}')
        auth_code = input('Enter authorization code or URL: ').strip()
        match = re.search(r'[?&]code=([^&]+)', auth_code)
        if match:
            auth_code = match[1]

        response = requests.post(
            'https://myanimelist.net/v1/oauth2/token', 
            {
                'client_id': self._client_id,
                'code': auth_code,
                'code_verifier': challenge,
                'grant_type': 'authorization_code'
            }
        )
        response.raise_for_status()
        self._update_tokens(response.json())

    def _refresh_tokens(self):
        response = requests.post(
            'https://myanimelist.net/v1/oauth2/token', 
            {
                'client_id': self._client_id,
                'grant_type': 'refresh_token',
                'refresh_token': self._refresh_token
            }
        )
        response.raise_for_status()
        self._update_tokens(response.json())

    def _update_tokens(self, tokens_response, *, save_to_file=True):
        self._access_token = tokens_response['access_token']
        self._refresh_token = tokens_response['refresh_token']

        # Save tokens to file
        if save_to_file:
            with open(self._tokens_file_path, 'w') as f:
                json.dump(tokens_response, f, indent=4)

    def _send_authenticated_request(self, request_method, url, headers=None, json_data=None, data=None):
        request_headers = {'Authorization': f'Bearer {self._access_token}'}
        if headers:
            request_headers.update(headers)
        r = requests.request(request_method, 'https://api.myanimelist.net/v2/'+url, headers=request_headers, json=json_data, data=data)

        if r.status_code == 401 and r.json()['error'] == 'invalid_token':
            print('Token expired, refreshing')
            self._refresh_tokens()
            return self._send_authenticated_request(request_method, url, json_data, data)

        if not r.ok:
            print(r.content.decode())
            r.raise_for_status()
        return r.json()


if __name__ == '__main__':
    u = MyAnimeListUser(input('Enter client ID: '), path.join(path.dirname(__file__), 'token.json')).get_user_info()
    print(u)
