from opgg.opgg import OPGG
from opgg.summoner import Summoner
from opgg.summoner import Game
from opgg.params import Region
from opgg.champion import ChampionStats
from opgg.champion import Champion
import csv

def main():
    opgg_obj = OPGG()

    with open("gameInfo.csv", mode="a", encoding="utf-8", newline="", buffering=1) as file:

        writer = csv.writer(file)

        with open("userList.txt", mode = "r", encoding="utf-8") as userList:
            for line in userList:

                print("On user: " + line)

                #Game ID, Game Version, Left side win?, (Player <#> Name, Player <#> Side, Player <#> Tier, Player <#> Division, Player <#> Position, Player <#> Champion ID, Player <#> Games on champ, Player <#> Champion Winrate for Current Patch, Player <#> Winrate, Player <#> Hotstreak)
                while True:
                    try:
                        summoner: Summoner = opgg_obj.search(line)
                    except Exception as e:
                        print(f'Excepion {e} occured')
                        continue
                    break
                
                while True:
                    try:
                        game = opgg_obj.get_recent_games(10, "ranked", False)
                    except Exception as e:
                        print(f'Exception {e} occured')
                        continue
                    break

                if(game):
                    for games in game:
                        print("Game started")
                        data = list()
                        
                        data.append(games.id)
                        data.append(games.version)
                        data.append(games.teams[0].game_stat.is_win)

                        blueTop = list()
                        blueJG = list()
                        blueMid = list()
                        blueADC = list()
                        blueSup = list()
                        redTop = list()
                        redJG = list()
                        redMid = list()
                        redADC = list()
                        redSup = list()

                        players = games.participants
                        for player in players:
                            name = player.summoner.game_name + '#' + player.summoner.tagline

                            while True:
                                try:
                                    summoner = opgg_obj.search(name)
                                except Exception as e:
                                    print(f'Exception {e} occured')
                                    continue
                                break

                            tempTeam = player.team_key
                            tempRole = player.position

                            if 'BLUE' in tempTeam and 'TOP' in tempRole:
                                blueTop.append(name)
                                blueTop.append(player.team_key)
                                blueTop.append(player.tier_info.tier)
                                blueTop.append(player.tier_info.division)
                                blueTop.append(player.position)
                                blueTop.append(player.champion_id)
                                blueTop.append(summoner.league_stats[0].win_rate)
                                blueTop.append(summoner.league_stats[0].is_hot_streak)
                            elif 'BLUE' in tempTeam and 'JUNGLE' in tempRole:
                                blueJG.append(name)
                                blueJG.append(player.team_key)
                                blueJG.append(player.tier_info.tier)
                                blueJG.append(player.tier_info.division)
                                blueJG.append(player.position)
                                blueJG.append(player.champion_id)
                                blueJG.append(summoner.league_stats[0].win_rate)
                                blueJG.append(summoner.league_stats[0].is_hot_streak)
                            elif 'BLUE' in tempTeam and 'MID' in tempRole:
                                blueMid.append(name)
                                blueMid.append(player.team_key)
                                blueMid.append(player.tier_info.tier)
                                blueMid.append(player.tier_info.division)
                                blueMid.append(player.position)
                                blueMid.append(player.champion_id)
                                blueMid.append(summoner.league_stats[0].win_rate)
                                blueMid.append(summoner.league_stats[0].is_hot_streak)
                            elif 'BLUE' in tempTeam and 'ADC' in tempRole:                             
                                blueADC.append(name)
                                blueADC.append(player.team_key)
                                blueADC.append(player.tier_info.tier)
                                blueADC.append(player.tier_info.division)
                                blueADC.append(player.position)
                                blueADC.append(player.champion_id)
                                blueADC.append(summoner.league_stats[0].win_rate)
                                blueADC.append(summoner.league_stats[0].is_hot_streak)
                            elif 'BLUE' in tempTeam and 'SUPPORT' in tempRole:                              
                                blueSup.append(name)
                                blueSup.append(player.team_key)
                                blueSup.append(player.tier_info.tier)
                                blueSup.append(player.tier_info.division)
                                blueSup.append(player.position)
                                blueSup.append(player.champion_id)
                                blueSup.append(summoner.league_stats[0].win_rate)
                                blueSup.append(summoner.league_stats[0].is_hot_streak)
                            elif 'RED' in tempTeam and 'TOP' in tempRole:                               
                                redTop.append(name)
                                redTop.append(player.team_key)
                                redTop.append(player.tier_info.tier)
                                redTop.append(player.tier_info.division)
                                redTop.append(player.position)
                                redTop.append(player.champion_id)
                                redTop.append(summoner.league_stats[0].win_rate)
                                redTop.append(summoner.league_stats[0].is_hot_streak)
                            elif 'RED' in tempTeam and 'JUNGLE' in tempRole:                             
                                redJG.append(name)
                                redJG.append(player.team_key)
                                redJG.append(player.tier_info.tier)
                                redJG.append(player.tier_info.division)
                                redJG.append(player.position)
                                redJG.append(player.champion_id)
                                redJG.append(summoner.league_stats[0].win_rate)
                                redJG.append(summoner.league_stats[0].is_hot_streak)
                            elif 'RED' in tempTeam and 'MID' in tempRole:                              
                                redMid.append(name)
                                redMid.append(player.team_key)
                                redMid.append(player.tier_info.tier)
                                redMid.append(player.tier_info.division)
                                redMid.append(player.position)
                                redMid.append(player.champion_id)
                                redMid.append(summoner.league_stats[0].win_rate)
                                redMid.append(summoner.league_stats[0].is_hot_streak)
                            elif 'RED' in tempTeam and 'ADC' in tempRole:                               
                                redADC.append(name)
                                redADC.append(player.team_key)
                                redADC.append(player.tier_info.tier)
                                redADC.append(player.tier_info.division)
                                redADC.append(player.position)
                                redADC.append(player.champion_id)
                                redADC.append(summoner.league_stats[0].win_rate)
                                redADC.append(summoner.league_stats[0].is_hot_streak)
                            else:                              
                                redSup.append(name)
                                redSup.append(player.team_key)
                                redSup.append(player.tier_info.tier)
                                redSup.append(player.tier_info.division)
                                redSup.append(player.position)
                                redSup.append(player.champion_id)
                                redSup.append(summoner.league_stats[0].win_rate)
                                redSup.append(summoner.league_stats[0].is_hot_streak)

                            tempTeam = ''
                            tempRole = ''

                        data.extend(blueTop)
                        data.extend(blueJG)
                        data.extend(blueMid)
                        data.extend(blueADC)
                        data.extend(blueSup)
                        data.extend(redTop)
                        data.extend(redJG)
                        data.extend(redMid)
                        data.extend(redADC)
                        data.extend(redSup)

                        writer.writerow(data)
                        print("Game finished")

                    print("Finished user: " + line)


if __name__ == "__main__":
    main()