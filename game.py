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
        return {"status": "waiting"}

    if waiting_player["user_id"] == user_id:
        return {"status": "already_waiting"}

    player1 = waiting_player
    player2 = {
        "user_id": user_id,
        "username": username
    }

    waiting_player = None

    match_id = f"{player1['user_id']}_{player2['user_id']}"

    batting = random.choice([1, 2])

    matches[match_id] = {
        "player1": player1,
        "player2": player2,
        "batting": batting,
        "score": 0,
        "target": None,
        "choices": {}
    }

    return {
        "status": "matched",
        "match_id": match_id,
        "player1": player1,
        "player2": player2,
        "batting": batting
    }


def get_match(match_id):
    return matches.get(match_id)


def submit_choice(match_id, user_id, choice):
    match = matches.get(match_id)

    if not match:
        return {"status": "not_found"}

    match["choices"][user_id] = choice

    if len(match["choices"]) < 2:
        return {"status": "waiting"}

    users = list(match["choices"].keys())

    choice1 = match["choices"][users[0]]
    choice2 = match["choices"][users[1]]

    match["choices"] = {}

    if choice1 == choice2:
        return {
            "status": "wicket",
            "choice1": choice1,
            "choice2": choice2
        }

    return {
        "status": "runs",
        "choice1": choice1,
        "choice2": choice2
    }
