import requests
import json
import time
import pdb
from typing import List, Dict, Any, Optional

from constants import *


# NOTE: Riot now encourages using Riot ID (Name#Tag) with the Account-v1 endpoint, 
# but the Summoner-v4 endpoint by name still works for League/TFT summoner names.
SUMMONER_URL = f"https://{REGIONAL_ROUTE}.api.riotgames.com/tft/summoner/v1/summoners/by-riot-id/{{summonerName}}/NA1"
# SUMMONER_URL = f"https://{REGIONAL_ROUTE}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{{summonerName}}/NA1?api_key={API_KEY}"
MATCH_IDS_URL = f"https://{REGIONAL_ROUTE}.api.riotgames.com/tft/match/v1/matches/by-puuid/{{puuid}}/ids"
LEAGUE_URL = f"https://{PLATFORM_ROUTE}.api.riotgames.com/tft/league/v1/entries/by-summoner/{{summonerId}}"

def get_api_data(url: str, params: Dict[str, Any] = None) -> Optional[Any]:
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

def calculate_lp_changes(summoner_name: str, count: int = 10):
    print(f"Getting Summoner ID and PUUID for '{summoner_name}'...")
    pdb.set_trace()
    summoner_data = get_api_data(SUMMONER_URL.format(summonerName=summoner_name))
    if not summoner_data: 
        print(f"*o* Summoner not Found Error!!")
        return []
    puuid = summoner_data.get('puuid')
    summoner_id = summoner_data.get('id')
    print(f"PUUID: {puuid[:8]}..., Summoner ID: {summoner_id[:8]}...")
    
    print(f"\nGetting last {count} Match IDs...")
    match_ids_url = MATCH_IDS_URL.format(puuid=puuid)
    match_ids = get_api_data(match_ids_url, params={'count': count})
    if not match_ids: return []
    print(f"-> Retrieved {len(match_ids)} match IDs.")
    print("\n3. Getting current League Entry data (LP/Wins/Losses)...")
    league_entries = get_api_data(LEAGUE_URL.format(summonerId=summoner_id))
    
    # Find the TFT Ranked entry
    ranked_entry = next((e for e in league_entries if e.get('queueType') == TFT_RANKED_QUEUE), None)
    if not ranked_entry:
        print("!!! Error: Player is not ranked in TFT or ranked data not found.")
        return []

    # Initialize a list to hold the final results
    results = []
    
    # The current state before processing the loop
    current_lp = ranked_entry['leaguePoints']
    current_wins = ranked_entry['wins']
    current_losses = ranked_entry['losses']
    print(f"-> Current LP: {current_lp}, Wins: {current_wins}, Losses: {current_losses}")
    
    print("\n4. Analyzing Matches and Calculating LP Changes...")
    
    # Iterate through match IDs in reverse order (oldest to newest) to correctly track LP changes
    # However, since we only have the CURRENT league data, we iterate newest to oldest, 
    # and calculate the PREVIOUS LP based on the game's placement.
    
    match_data_list: List[Dict[str, Any]] = []
    for match_id in match_ids:
        match_detail = get_api_data(MATCH_DETAIL_URL_TEMPLATE.format(matchId=match_id), headers=headers)
        if match_detail:
            # Find the player's participant data within the match
            participant_data = next((
                p for p in match_detail['info']['participants'] if p['puuid'] == puuid
            ), None)
            
            if participant_data:
                match_data_list.append({
                    'match_id': match_id,
                    'placement': participant_data['placement'],
                    'game_end_time': match_detail['info']['game_datetime']
                })
        
    # Process from newest match (index 0) to oldest
    for i, match in enumerate(match_data_list):
        placement = match['placement']
        
        # This is the LP *after* this match was played.
        lp_after_match = current_lp 
        
        # The first match (i=0) is the *newest*. The rest of the LP changes 
        # are calculated by comparing current_lp to the *next* match's LP.
        if i == len(match_data_list) - 1:
            # This is the OLDEST match. We cannot calculate the LP before it, 
            # so we just mark the change as unknown.
            lp_change = "N/A"
            lp_before_match = "N/A"
        else:
            # The LP *before* this match is the LP *after* the next (older) match.
            lp_before_match = match_data_list[i+1].get('lp_after_match')
            
            if lp_before_match is not None and lp_before_match != "N/A":
                lp_change = lp_after_match - lp_before_match
            else:
                lp_change = "N/A"

        # Store the calculated LP after this match so it can be used for the next iteration
        # This simulates having a database of LP snapshots after each game.
        match_data_list[i]['lp_after_match'] = lp_after_match
        
        results.append({
            'Match ID': match['match_id'],
            'Placement': placement,
            'LP After Match': lp_after_match,
            'LP Before Match': lp_before_match,
            'LP Change': lp_change,
        })
        
        # Prepare for the next iteration (older match).
        # We assume the LP before this match is the one we want to calculate 
        # for the previous iteration's 'lp_after_match'.
        # We need to *approximate* the LP lost/gained to estimate the LP before the current game.
        # However, since we can't reliably predict LP gain/loss without tracking data, 
        # the best we can do is use the "after" LP of the next match in the history.
        # This means the LP change can only be calculated for all but the *oldest* game.
        current_lp = lp_before_match if lp_before_match != "N/A" else current_lp # Use the next known 'before' LP

    return results

# --- Execution ---
if __name__ == "__main__":
    match_data_with_lp = calculate_lp_changes(PLAYER_NAME, count=5)
    
    if match_data_with_lp:
        print("\n=======================================================")
        print(f" LP Change Approximation for {PLAYER_NAME} (Last {len(match_data_with_lp)} games)")
        print("=======================================================")
        
        # Print the results in a cleaner, chronological order (oldest match first)
        for match in reversed(match_data_with_lp):
            print(f"Match: {match['Match ID']}")
            print(f"  Placement: {match['Placement']}")
            print(f"  LP Change: {match['LP Change']}")
            print(f"  (LP After: {match['LP After Match']}, LP Before: {match['LP Before Match']})")
            print("---")