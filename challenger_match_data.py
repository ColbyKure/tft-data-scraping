import requests
import json
import time
import pdb
from constants import *

CHALLENGER_URL = f"https://{PLATFORM_ROUTE}.api.riotgames.com/tft/league/v1/challenger"
MATCH_IDS_URL_TEMPLATE = f"https://{REGIONAL_ROUTE}.api.riotgames.com/tft/match/v1/matches/by-puuid/{{puuid}}/ids?count=1"
MATCH_DETAIL_URL_TEMPLATE = f"https://{REGIONAL_ROUTE}.api.riotgames.com/tft/match/v1/matches/{{matchId}}"


def get_challenger_match_data(api_key):
    headers = {
        "X-Riot-Token": api_key
    }
    print(f"Recieved API key ({api_key})...")
    pdb.set_trace()
    try:
        response = requests.get(CHALLENGER_URL, headers=headers)
        response.raise_for_status()
        challenger_data = response.json()
        print(f"Challenger Data Recieved...")
        
        if not challenger_data.get('entries'):
            print("Error: No Challenger players found.")
            return

        challenger_puuid = challenger_data['entries'][0]['puuid']
        print(f"-> Found Challenger PUUID: {challenger_puuid[:8]}...")
    except requests.exceptions.RequestException as e:
        print(f"Exception in getting Challenger player data: {e}")
        return

    # Get the latest Match ID for that player
    match_ids_url = MATCH_IDS_URL_TEMPLATE.format(puuid=challenger_puuid)
    time.sleep(SLEEP_TIME)
    try:
        response = requests.get(match_ids_url, headers=headers)
        response.raise_for_status()
        match_ids = response.json()
        
        if not match_ids:
            print("Error: No recent matches found for this player.")
            return

        match_id = match_ids[0]
        print(f"-> Found Match ID: {match_id}")
    except requests.exceptions.RequestException as e:
        print(f"Error in Step 2 (Match IDs): {e}")
        return

    match_detail_url = MATCH_DETAIL_URL_TEMPLATE.format(matchId=match_id)
    time.sleep(SLEEP_TIME)
    try:
        response = requests.get(match_detail_url, headers=headers)
        response.raise_for_status()
        match_data = response.json()
        
        print(f"-> Successfully retrieved full match data for {match_id}. Data size: {len(response.text) / 1024:.2f} KB")
        return match_data
    except requests.exceptions.RequestException as e:
        print(f"Error in Step 3 (Match Details): {e}")
        return

if __name__ == "__main__":
    full_match_data = get_challenger_match_data(API_KEY)
    pdb.set_trace()
    if full_match_data:
        for i in range(8):
            # Example of how to access a unit's data from the first participant
            first_participant_units = full_match_data['info']['participants'][i]['units']
            print("\n--- UNITS AND ITEMS OF PLAYER {i} (Begin)")
            for unit in first_participant_units:
                items_names = ", ".join(unit['itemNames'])
                print(f"  Unit: {unit['character_id']}, Tier: {unit['tier']}, Items: [{items_names}]")
            print("\n--- UNITS AND ITEMS OF PLAYER {i} (END)")
            