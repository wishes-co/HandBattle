import random

waiting_player = None
matches = {}


def join_match(user_id, username):
    global waiting_player

    if waiting_player is None:
        waiting_player = {
            "user_id": user_id,
            "username": username
        }

        return {
            "status": "waiting"
        }

    if waiting_player["user_id"] == user_id:
        return {
            "status": "already_waiting"
        }

    player1 = waiting_player
    player2 = {
        "user_id": user_id,
        "username": username
    }

    waiting_player = None

    match_id = f"{player1['user_id']}_{player2['user_id']}"

    matches[match_id] = {
        "player1": player1,
        "player2": player2,
        "score1": 0,
        "score2": 0,
        "wickets1": 0,
        "wickets2": 0,
        "innings": 1,
        "batting": player1["user_id"]
    }

    return {
        "status": "matched",
        "match_id": match_id,
        "player1": player1,
        "player2": player2
    }


def get_match(match_id):
    return matches.get(match_id)


def toss():
    return random.choice(["player1", "player2"])
