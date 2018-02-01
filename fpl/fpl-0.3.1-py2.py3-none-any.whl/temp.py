import fpl
import json

def build_form():
    """
    Returns dictionary with the amount of goals scored by each player.
    """
    player_form = {}

    for player in players:
        player_id = player["id"]
        goals_scored = player["goals_scored"]
        player_form[player_id] = goals_scored

    return player_form

if __name__ == '__main__':
    fpl = fpl.FPL()
    players = fpl.players
    player_form = build_form()
    sorted_players = sorted(player_form.items(), key=lambda x:x[1],
        reverse=True)

    for player in sorted_players[:10]:
        print("Player with id {} has scored {} goals!".format(player[0],
            player[1]))
    