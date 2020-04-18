import re
import wptools
import pickle
from tqdm import tqdm

import pandas as pd


def get_player_names(path):
    data = pd.read_csv(path)
    return data.player_name.drop_duplicates().to_frame()


def get_wikipedia_page(player):
    # print("Player name: {}".format(player))
    try:
        p_page = wptools.page(player, silent=True).get_parse(show=False)
    except Exception as e:
        raise ValueError(e) from None
    # print(p_page.data['title'])
    return p_page


def extract_infobox_from_wp(players, pickle_path):
    player_stats = {}
    for player in tqdm(players):
        try:
            page = get_wikipedia_page(player)
            player_stats[player] = page.data['infobox']
        except ValueError:
            player_stats[player] = None
    with open(pickle_path, "wb") as f:
        pickle.dump(player_stats, f)


def read_players_infobox(pickle_path):
    with open(pickle_path, "rb") as f:
        player_stats = pickle.load(f)
    return player_stats


def get_player_height(players, player_stats):
    height_list = []
    for player in players.player_name:
        if player_stats[player] is not None:
            if 'height' in player_stats[player].keys():
                height_list.append(player_stats[player]['height'])
                continue
        height_list.append(None)
    players['height'] = pd.Series(height_list)
    return players


def get_player_nationalities(players, player_stats):
    national_team_list = []
    for player in tqdm(players.player_name):
        if player in player_stats.keys() and player_stats[player] is not None:
            latest_national_team = 1
            while True:
                try:
                    player_stats[player]["nationalteam{}".format(latest_national_team)]
                except KeyError:
                    latest_national_team -= 1
                    break
                latest_national_team += 1
            if latest_national_team == 0:
                national_team_list.append(None)
                continue
            s = player_stats[player]["nationalteam{}".format(latest_national_team)]
            try:
                regex_s = re.search("\|(.*)\]\]", s)
                national_team_list.append(regex_s.group(1))
            except AttributeError:
                national_team_list.append(s)
        else:
            national_team_list.append(None)
    players['nationality'] = national_team_list
    return players


def get_player_goals(players, player_stats):
    goals_list = []
    for player in tqdm(players.player_name):
        if player in player_stats.keys() and player_stats[player] is not None:
            latest_club_num = 1
            goals = 0
            while True:
                try:
                    goal_str = player_stats[player]["goals{}".format(latest_club_num)]
                    try:
                        goals += int(goal_str)
                    except ValueError:
                        goals += 0
                except KeyError:
                    latest_club_num -= 1
                    break
                latest_club_num += 1
            if latest_club_num == 0:
                goals_list.append(None)
                continue
            goals_list.append(goals)
        else:
            goals_list.append(None)
    players['goals'] = goals_list
    return players


if __name__ == "__main__":
    players = get_player_names(path="data/transfers1.2.csv")
    pickle_path = "data/player_infobox_data.pkl"

    ''' Extract infoboxes from wikipedia pages of players '''
#    extract_infobox_from_wp(players, pickle_path)

    ''' Read from saved wikipedia page infoboxes '''
    player_stats = read_players_infobox(pickle_path)

    ''' Get player heights '''
    players = get_player_height(players, player_stats)

    ''' Get player nationalities '''
    players = get_player_nationalities(players, player_stats)

    ''' Get player goals '''
    players = get_player_goals(players, player_stats)

    ''' Write to disk '''
    players.to_csv("data/player_wikipedia_stats.csv", index=False)
