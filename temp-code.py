import requests
import json
import time
import pdb


# Getting summoner name
GAME_NAME = "kureboy001"
TAGLINE = 'NA1'
API_KEY = 'RGAPI-68a707de-5949-4831-91fa-b61ed0208d80'
REGIONAL_ROUTE = 'americas'
GET_BASE_URL = f'https://{REGIONAL_ROUTE}.api.riotgames.com'
GET_ACCOUNT_BY_RIOT_ID = f'{GET_BASE_URL}/riot/account/v1/accounts/by-riot-id/{GAME_NAME}/{TAGLINE}'
GET_LEAGUE_BY_PUUID = f'{GET_BASE_URL}/tft/league/v1/by-puuid/{{puuid}}'
GET_MATCHES_BY_PUUID = f'{GET_BASE_URL}/tft/match/v1/matches/by-puuid/{{puuid}}/ids?start=0&count=100'
GET_MATCH_DATA_BY_MATCH_ID = f'{GET_BASE_URL}/tft/match/v1/matches/{{matchId}}'
GET_CHALLENGER = f'{GET_BASE_URL}/tft/league/v1/challenger'

def get_api_data(url):
    headers = {"X-Riot-Token": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"*o* HTTP Error {e.response.status_code} on URL: {url} | Message: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"*o* Request Error: {e}")
        return None


acc = get_api_data(GET_ACCOUNT_BY_RIOT_ID)
print(f"Recieved ({acc['gameName']}#{acc['tagLine']}) data with puuid ({acc['puuid']})")
puuid = acc['puuid']
league = get_api_data(GET_LEAGUE_BY_PUUID.format(puuid=puuid))
challengers = get_api_data(GET_CHALLENGER)
matches = get_api_data(GET_MATCHES_BY_PUUID.format(puuid=puuid))
print(len(matches), ' matches found')
match = matches[0]
match_data = get_api_data(GET_MATCH_DATA_BY_MATCH_ID.format(matchId=match))
pdb.set_trace()