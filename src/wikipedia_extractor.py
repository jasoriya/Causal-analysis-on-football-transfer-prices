import wptools
import pickle

import pandas as pd


def get_player_names(path):
    data = pd.read_csv(path)
    return data.player_name.drop_duplicates()


def get_wikipedia_page(player):
    print("Player name: {}".format(player))
    p_page = wptools.page(player, silent=True).get_parse(show=False)
#    print(p_page.data['title'])
    return p_page


def extract_infobox_from_wp(players, pickle_path):
    player_stats = {}
    for player in players:
        try:
            page = get_wikipedia_page(player)
            player_stats[player] = page.data['infobox']
        except Exception:
            print("failed, page not found: {}".format(player))
            player_stats[player] = None
    with open(pickle_path, "wb") as f:
        pickle.dump(player_stats, f)


def read_players_infobox(pickle_path):
    with open(pickle_path, "rb") as f:
        player_stats = pickle.load(f)
    return player_stats


if __name__ == "__main__":
    players = get_player_names(path="../data/transfers1.2.csv")
    pickle_path = "../data/player_infobox_data.pkl"
    extract_infobox_from_wp(players, pickle_path)
#    player_stats = read_players_infobox(pickle_path)
