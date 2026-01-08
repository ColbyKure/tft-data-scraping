import requests
import json
import time
import pdb
from datetime import datetime


# ====================================================
API_KEY = 'RGAPI-bc47e1aa-4b40-4410-b474-14aaff9ade1c'
# ====================================================

# ===== CONSTANTS =====
GAME_NAME = "kureboy001"
TAGLINE = 'NA1'
REGIONAL_ROUTE = 'americas'
GET_BASE_URL = f'https://{REGIONAL_ROUTE}.api.riotgames.com'
GET_ACCOUNT_BY_RIOT_ID = f'{GET_BASE_URL}/riot/account/v1/accounts/by-riot-id/{GAME_NAME}/{TAGLINE}'
GET_LEAGUE_BY_PUUID = f'{GET_BASE_URL}/tft/league/v1/by-puuid/{{puuid}}'
GET_MATCHES_BY_PUUID = f'{GET_BASE_URL}/tft/match/v1/matches/by-puuid/{{puuid}}/ids?start=0&count=100'
GET_MATCHES_BY_PUUID_WITH_START_TIME = f'{GET_BASE_URL}/tft/match/v1/matches/by-puuid/{{puuid}}/ids?startTime={{epoch_time}}'
GET_MATCH_DATA_BY_MATCH_ID = f'{GET_BASE_URL}/tft/match/v1/matches/{{matchId}}'
GET_CHALLENGER = f'{GET_BASE_URL}/tft/league/v1/challenger'
EPOCH_TIME_SET_16_RELEASE = 1764748800
SET_16_RELEASE_DATETIME = datetime(2024,12,3)


# ===== FUNCTIONS =====
def query_riot_api(url):
    headers = {"X-Riot-Token": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error {e.response.status_code} on URL: {url} | Message: {e}")
        print("Try to refresh dev key: https://developer.riotgames.com/")
        return
    except requests.exceptions.RequestException as e:
        print(f"*o* Request Error: {e}")
        return

def get_epoch_time_from_datetime(dt_obj):
    if not isinstance(dt_obj, datetime):
        raise ValueError("Input must be a datetime object.")
    return int(dt_obj.timestamp())



# ===== MAIN CODE =====
# league = query_riot_api(GET_LEAGUE_BY_PUUID.format(puuid=puuid))      # GETS LEAGUE/RANK BY PUUID
# challengers = query_riot_api(GET_CHALLENGER)      # GETS CHALLENGER PLAYER IDS


acc = query_riot_api(GET_ACCOUNT_BY_RIOT_ID)
print(f"Recieved ({acc['gameName']}#{acc['tagLine']}) data with puuid ({acc['puuid']})\n")
puuid = acc['puuid']
tft_set_16_release_epochtime = get_epoch_time_from_datetime(SET_16_RELEASE_DATETIME)
matches_this_set = query_riot_api(GET_MATCHES_BY_PUUID_WITH_START_TIME.format(puuid=puuid,epoch_time=tft_set_16_release_epochtime))
match = matches_this_set[0]
match_data_first = query_riot_api(GET_MATCH_DATA_BY_MATCH_ID.format(matchId=match))
match = matches_this_set[-1]
match_data_last = query_riot_api(GET_MATCH_DATA_BY_MATCH_ID.format(matchId=match))
assert(match_data_last['info']['tft_set_number'] == match_data_first['info']['tft_set_number'])     # therefore all data is from same set
curr_set_number = match_data_last['info']['tft_set_number']
print(f"{GAME_NAME} played {len(matches_this_set)} matches in set {curr_set_number}")

pdb.set_trace()