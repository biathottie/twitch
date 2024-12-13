import csv
import json
from types import NoneType
import requests
import time
import pickle
import os

from rich.console import Console
from rich.markdown import Markdown
from rich.progress import track
from rich.theme import Theme
from rich.table import Table

from dotenv import find_dotenv, load_dotenv
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from opgg.v2 import search_result
from opgg.v2.opgg import OPGG
from opgg.v2.params import Region
from opgg.v2.search_result import SearchResult
from opgg.v2.summoner import Summoner
from opgg.v2.types.response import LiveGameResponse
from opgg.v2.season import TierInfo

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

#Touch
key = os.getenv('RIOT_API_KEY')
accountNamesToLookAt = [['Air Coots','Prime'],['Glenn Danzig SMP','demon'],['SEN TenZ','81619'],['Karasmai Kayn','NA1'],['I will trade','NA1']]
region = ''

#Don't touch
puuids = []
liveGame = []

blueSideWinProb = 0.0
redSideWinProb = 0.0

console = Console(highlight=False)

def getPUUIDS():

    MARKDOWN = '# Converting usernames into PUUIDs'
    md = Markdown(MARKDOWN, style='bold')
    console.print(md)

    for account in track(accountNamesToLookAt, description='[bold]Progress...', style='bold white', complete_style='bold cyan', finished_style='bold cyan'):
        getAccount = f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{account[0]}/{account[1]}?api_key={key}'

        try:
            response = requests.get(getAccount)

            if(response.status_code == 200):
                posts = response.json()
                puuids.append(posts['puuid'])
            else:
                console.print('Error: ', response.status_code)
        except requests.exceptions.RequestException as e:
            return 'Error', e

def getLiveGame():

    console.print('\n')
    MARKDOWN = '# Going through list of PUUIDs'
    md = Markdown(MARKDOWN, style='bold')
    console.print(md)

    for puuid in puuids:
        getLiveGameCall = f'https://na1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}?api_key={key}'

        try:
            response = requests.get(getLiveGameCall)

            if(response.status_code == 200):
                liveGame = response.json()
                console.print('[bold][red]Found live game for PUUID: [/red]' + puuid)
                return liveGame
            else:
                console.print('Error: ', response.status_code)
        except requests.exceptions.RequestException as e:
            console.print('Error: ', e)
            return 'Error', e

    return None
        
def getData(liveGame):

    opgg_obj = OPGG()

    if(len(liveGame) != 0):
        
        #Update the first player we come across to make sure their current game will show as live
        while True:
            try:
                tempName = liveGame['participants'][0]['riotId']
                searchResult: list[SearchResult] = opgg_obj.search(tempName, region=Region.NA)
            except Exception as e:
                print(f'Excepion {e} occured')
                continue
            break
    
        opgg_obj.update(searchResult[0])

        live_game: LiveGameResponse = opgg_obj.get_live_game(searchResult[0]).data

        data = list()

        #Only the patch # matters, the rest will get          
        data.append(live_game.game_id)
        data.append('14.23')
        data.append('TRUE')

        blueTop, blueJG, blueMid, blueADC, blueSup, redTop, redJG, redMid, redADC, redSup = ([] for i in range(10))
        playerInfo = [blueTop, blueJG, blueMid, blueADC, blueSup, redTop, redJG, redMid, redADC, redSup]

        for i in track(range(10), description='[bold]Getting stats for players...', style='bold white', complete_style='bold cyan', finished_style='bold cyan', pulse_style='bold cyan'):
            
            playerTeam = live_game.participants[i].team_key
            playerRole = live_game.participants[i].position

            player_index_map = {
                ('BLUE', 'TOP'): 0,
                ('BLUE', 'JUNGLE'): 1,
                ('BLUE', 'MID'): 2,
                ('BLUE', 'ADC'): 3,
                ('BLUE', 'SUPPORT'): 4,
                ('RED', 'TOP'): 5,
                ('RED', 'JUNGLE'): 6,
                ('RED', 'MID'): 7,
                ('RED', 'ADC'): 8,
                ('RED', 'SUPPORT'): 9
            }
            playerIndex = player_index_map.get((playerTeam, playerRole), 9)

            playerName = live_game.participants[i].summoner.game_name + '#' + live_game.participants[i].summoner.tagline
            playerInfo[playerIndex].append(playerName)
            playerInfo[playerIndex].append(playerTeam)
            #playerInfo[playerIndex].append(live_game.participants[i].tier_info.tier.upper())

            #temp
            playerInfo[playerIndex].append('SILVER')

            playerInfo[playerIndex].append(1)
            playerInfo[playerIndex].append(playerRole)
            playerInfo[playerIndex].append(live_game.participants[i].champion_id)

            try:
                playerInfo[playerIndex].append(((live_game.participants[i].summoner.league_stats[0].win) / (live_game.participants[i].summoner.league_stats[0].win + live_game.participants[i].summoner.league_stats[0].lose)) * 100)
                playerInfo[playerIndex].append(live_game.participants[i].summoner.league_stats[0].is_hot_streak)
            except TypeError:
                playerInfo[playerIndex].append(50.0)
                playerInfo[playerIndex].append(False)
            except IndexError:
                playerInfo[playerIndex].append(50.0)
                playerInfo[playerIndex].append(False)
        
        for player in playerInfo:
            data.extend(player)

        #Write to CSV
        with open("gameInfo.csv", mode="a", encoding="utf-8", newline="", buffering=1) as file:
            writer = csv.writer(file)
            writer.writerow(data)

def manipulateData():

        console.print('\n')
        MARKDOWN = '# Manipulating Data'
        md = Markdown(MARKDOWN, style='bold')
        console.print(md)

        #Manipulation time
        df = pd.read_csv('gameInfo.csv')
        df = df.dropna()
        
        #Change champ ID to champ name, making it more readable
        #If broken you will need to get updated champion_data.json from riot website
        champ_data = json.load(open('champion_data.json', encoding="utf8"))

        df['BlueTopChampName'] = df['BlueTopChampID'].apply(lambda x: champ_data['data'][str(x)]['name'])
        df['BlueJungleChampName'] = df['BlueJungleChampID'].apply(lambda x: champ_data['data'][str(x)]['name'])
        df['BlueMidChampName'] = df['BlueMidChampID'].apply(lambda x: champ_data['data'][str(x)]['name'])
        df['BlueADCChampName'] = df['BlueADCChampID'].apply(lambda x: champ_data['data'][str(x)]['name'])
        df['BlueSupportChampName'] = df['BlueSupportChampID'].apply(lambda x: champ_data['data'][str(x)]['name'])

        df['RedTopChampName'] = df['RedTopChampID'].apply(lambda x: champ_data['data'][str(x)]['name'])
        df['RedJungleChampName'] = df['RedJungleChampID'].apply(lambda x: champ_data['data'][str(x)]['name'])
        df['RedMidChampName'] = df['RedMidChampID'].apply(lambda x: champ_data['data'][str(x)]['name'])
        df['RedADCChampName'] = df['RedADCChampID'].apply(lambda x: champ_data['data'][str(x)]['name'])
        df['RedSupportChampName'] = df['RedSupportChampID'].apply(lambda x: champ_data['data'][str(x)]['name'])

        #Drop champID columns
        df = df[['GameVersion', 'BlueSideWin', 'BlueTopRank', 'BlueTopWinrate', 'BlueTopWinStreak', 'BlueTopChampName', 'BlueJungleRank', 'BlueJungleWinrate', 'BlueJungleWinStreak', 'BlueJungleChampName', 'BlueMidRank', 'BlueMidWinrate', 'BlueMidWinStreak', 'BlueMidChampName', 'BlueADCRank', 'BlueADCWinrate', 'BlueADCWinStreak', 'BlueADCChampName', 'BlueSupportRank', 'BlueSupportWinrate', 'BlueSupportWinStreak', 'BlueSupportChampName', 'RedTopRank', 'RedTopWinrate', 'RedTopWinStreak', 'RedTopChampName', 'RedJungleRank', 'RedJungleWinrate', 'RedJungleWinStreak', 'RedJungleChampName', 'RedMidRank', 'RedMidWinrate', 'RedMidWinStreak', 'RedMidChampName', 'RedADCRank', 'RedADCWinrate', 'RedADCWinStreak', 'RedADCChampName', 'RedSupportRank', 'RedSupportWinrate', 'RedSupportWinStreak', 'RedSupportChampName']]

        #Create boolean columns for each character in the game per team, 1 if it is on that specified team in current game, 0 if not. 10 total 1's per row
        encodingsBlue = [pd.get_dummies(df[col], prefix='Blue', dtype=int) for col in ['BlueTopChampName', 'BlueJungleChampName', 'BlueMidChampName', 'BlueADCChampName', 'BlueSupportChampName']]
        combined_dfBlue = sum(encodingsBlue)

        encodingsRed = [pd.get_dummies(df[col], prefix='Red', dtype=int) for col in ['RedTopChampName', 'RedJungleChampName', 'RedMidChampName', 'RedADCChampName', 'RedSupportChampName']]
        combined_dfRed = sum(encodingsRed)

        df = df.join(combined_dfBlue).join(combined_dfRed)

        #Drop champ name now that dummy columns are created
        df = df.drop(['BlueTopChampName', 'BlueJungleChampName', 'BlueMidChampName', 'BlueADCChampName', 'BlueSupportChampName', 'RedTopChampName', 'RedJungleChampName', 'RedMidChampName', 'RedADCChampName', 'RedSupportChampName'], axis=1)

        #Change rank text to integer represenatation
        pd.set_option("future.no_silent_downcasting", True)
        df['BlueTopRank'] = df['BlueTopRank'].replace('UNRANKED', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['BlueJungleRank'] = df['BlueJungleRank'].replace('UNRANKED', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['BlueMidRank'] = df['BlueMidRank'].replace('UNRANKED', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['BlueADCRank'] = df['BlueADCRank'].replace('UNRANKED', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['BlueSupportRank'] = df['BlueSupportRank'].replace('UNRANKED', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)

        df['RedTopRank'] = df['RedTopRank'].replace('UNRANKED', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['RedJungleRank'] = df['RedJungleRank'].replace('UNRANKED', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['RedMidRank'] = df['RedMidRank'].replace('UNRANKED', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['RedADCRank'] = df['RedADCRank'].replace('UNRANKED', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['RedSupportRank'] = df['RedSupportRank'].replace('UNRANKED', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)

        #Don't need since we already made classifier
        df = df.drop(['GameVersion'], axis=1)
        df = df.drop(['BlueSideWin'], axis=1)

        console.print('\n')
        console.print(df.tail(1))

        with open('classifier.pkl', 'rb') as f:
            clf = pickle.load(f)

        predict = clf.predict(df.tail(1))
        probability = clf.predict_proba(df.tail(1))

        redSideWinProb = probability[0][0]
        blueSideWinProb = probability[0][1]

        result = ''
        if(True in predict):
            result = 'True'
        else:
            result = 'False'

        console.print('\n')
        MARKDOWN = '# Blue side predicted to win?'
        md = Markdown(MARKDOWN, style='bold')
        console.print(md)
        
        MARKDOWN = f'## {result}'
        md = Markdown(MARKDOWN, style='bold')
        console.print(md)

        MARKDOWN = f'## Red side win probability: {redSideWinProb}'
        md = Markdown(MARKDOWN, style='bold red')
        console.print(md)

        MARKDOWN = f'## Blue side win probability: {blueSideWinProb}'
        md = Markdown(MARKDOWN, style='bold cyan')
        console.print(md)

        return result

if __name__ == '__main__':
    
    MARKDOWN = '# Twitch Predictor for League'
    md = Markdown(MARKDOWN, style='bold cyan')
    console.print(md)

    MARKDOWN = '### by biathottie'
    md = Markdown(MARKDOWN, style='bold')
    console.print(md)

    console.print('\n')

    getPUUIDS()
    liveGame = getLiveGame()

    if liveGame is not None:
        getData(liveGame)
        formattedData = manipulateData()