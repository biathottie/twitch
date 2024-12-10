import csv
import json
from types import NoneType
import requests
import time
import pickle

from rich.console import Console
from rich.markdown import Markdown
from rich.progress import track
from rich.theme import Theme
from rich.table import Table

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from opgg.v2.opgg import OPGG
from opgg.v2.params import Region
from opgg.v2.search_result import SearchResult
from opgg.v2.summoner import Summoner

#Touch
key = 'RGAPI-98d5f5ae-36e8-4020-b89c-9a2b9d14079e'
accountNamesToLookAt = [['Air Coots','Prime'],['SEN TenZ','81619'],['Glenn Danzig SMP','demon'],['Karasmai Kayn','NA1'],['I will trade','NA1']]
region = ''

#Don't touch
puuids = []
liveGame = []

blueSideWinProb = 0.0
redSideWinProb = 0.0

chromeOptions = Options()
chromeOptions.add_argument("--log-level=3")
chromeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])

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

        #Scrape opgg to get info that isn't available in riot api or opgg.py - mainly their role
        #TEMPORARY until opgg.py adds live game lookup
        newName = tempName.replace('#','-').replace(' ','%20')
        url = f'https://www.op.gg/summoners/na/{newName}/ingame'
        
        driver = webdriver.Chrome(options=chromeOptions)
        driver.get(url)

        time.sleep(5)
        
        row_data = []
        rank_data = []
        table_bodys = driver.find_elements(By.TAG_NAME, "tbody")

        for table in table_bodys:
            table_rows = table.find_elements(By.TAG_NAME, "tr")

            for row in table_rows:
                table_data = row.find_elements(By.TAG_NAME, "td")
                for data in table_data:
                    dataClass = data.get_attribute('class')
                    if('Level' in data.text and '#' in data.text):
                        row_data.append(data.text)
                    if('current-rank' in dataClass):
                        if('Level' in data.text):
                            rank_data.append('UNRANKED')
                        else:
                            rank_data.append(data.text)

        driver.close()

        finalNames = []
        for name in row_data:
            index = name.rfind('Level')
            finalNames.append(name[:index - 1])

        ranks = []
        for rank in rank_data:
            index = rank.find(' ')
            ranks.append(rank[:index].upper())

        #Start building the data list for live game
        data = list()

        #Only the patch # matters, the rest will get          
        data.append(liveGame['gameId'])
        data.append('14.23')
        data.append('TRUE')

        #Make lists for each player in game, populate into master list
        blueTop, blueJG, blueMid, blueADC, blueSup, redTop, redJG, redMid, redADC, redSup = ([] for i in range(10))
        playerInfo = [blueTop, blueJG, blueMid, blueADC, blueSup, redTop, redJG, redMid, redADC, redSup]

        console.print()

        #Iterate through each player in list, populate with info pertaining to them
        for inx, player in track(enumerate(playerInfo), description='[bold]Getting stats for players...', style='bold white', complete_style='bold cyan', finished_style='bold cyan', pulse_style='bold cyan'):
            
            player.append(finalNames[inx])
            player.append('BLUE') if inx < 5 else player.append('RED')
            player.append(ranks[inx])
            player.append(1)
            if(inx == 0 or inx == 5):
                player.append('TOP')
            elif(inx == 1 or inx == 6):
                player.append('JUNGLE')
            elif(inx == 2 or inx == 7):
                player.append('MIDDLE')
            elif(inx == 3 or inx == 8):
                player.append('ADC')
            else:
                player.append('SUPPORT')

            for val in liveGame['participants']:
                if(finalNames[inx] in val['riotId']):
                    #print(val['championId'])
                    player.append(int(val['championId']))
            
            while True:
                try:
                    currentSummoner: list[SearchResult] = opgg_obj.search(finalNames[inx], region=Region.NA, returns='profile')
                except Exception as e:
                    print(f'Exception {e} occured')
                    continue
                break
            
            try:
                player.append(((currentSummoner[0].summoner.league_stats[0].win) / (currentSummoner[0].summoner.league_stats[0].win + currentSummoner[0].summoner.league_stats[0].lose)) * 100)
                player.append(currentSummoner[0].summoner.league_stats[0].is_hot_streak)
            except TypeError:
                player.append(50.0)
                player.append(False)
            
            
            # if(currentSummoner[0].summoner.league_stats[0].win is not NoneType and currentSummoner[0].summoner.league_stats[0].lose is not NoneType):
            #     player.append(((currentSummoner[0].summoner.league_stats[0].win) / (currentSummoner[0].summoner.league_stats[0].win + currentSummoner[0].summoner.league_stats[0].lose)) * 100)
            #     player.append(currentSummoner[0].summoner.league_stats[0].is_hot_streak)
            # else:
            #     player.append(50.0)
            #     player.append(False)

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

        #console.print('\n\nManipulating Data', style='bold cyan')

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
        df['BlueTopRank'] = df['BlueTopRank'].replace('UNRANKED', 0).replace('UNRANKE', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['BlueJungleRank'] = df['BlueJungleRank'].replace('UNRANKED', 0).replace('UNRANKE', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['BlueMidRank'] = df['BlueMidRank'].replace('UNRANKED', 0).replace('UNRANKE', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['BlueADCRank'] = df['BlueADCRank'].replace('UNRANKED', 0).replace('UNRANKE', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['BlueSupportRank'] = df['BlueSupportRank'].replace('UNRANKED', 0).replace('UNRANKE', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)

        df['RedTopRank'] = df['RedTopRank'].replace('UNRANKED', 0).replace('UNRANKE', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['RedJungleRank'] = df['RedJungleRank'].replace('UNRANKED', 0).replace('UNRANKE', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['RedMidRank'] = df['RedMidRank'].replace('UNRANKED', 0).replace('UNRANKE', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['RedADCRank'] = df['RedADCRank'].replace('UNRANKED', 0).replace('UNRANKE', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)
        df['RedSupportRank'] = df['RedSupportRank'].replace('UNRANKED', 0).replace('UNRANKE', 0).replace('IRON', 1).replace('BRONZE', 2).replace('SILVER', 3).replace('GOLD', 4).replace('PLATINUM', 5).replace('EMERALD', 6).replace('DIAMOND', 7).replace('MASTER', 8).replace('GRANDMASTER', 9).replace('CHALLENGER', 10)

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

# def predictGame(game):

        # with open('classifier.pkl', 'rb') as f:
        #     clf = pickle.load(f)

        # predict = clf.predict(game)
        # result = ''
        # if('True' in predict):
        #     result = 'True'
        # else:
        #     result = 'False'
        
        # print('\n\n================================')
        # print('Blue side predicted to win?')
        # print(result)
        # print('================================')

        # return result

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