import random

waiting_player = None
matches = {}

MAX_WICKETS = 3


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

        "score1": 0,
        "score2": 0,

        "wickets1": 0,
        "wickets2": 0,

        "innings": 1,

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

    # Same number = wicket
    if choice1 == choice2:

        if match["batting"] == 1:
            match["wickets1"] += 1
            wickets = match["wickets1"]
        else:
            match["wickets2"] += 1
            wickets = match["wickets2"]

        # Innings ends
        if wickets >= MAX_WICKETS:

            if match["innings"] == 1:

                if match["batting"] == 1:
                    target = match["score1"] + 1
                    match["target"] = target
                    match["batting"] = 2
                else:
                    target = match["score2"] + 1
                    match["target"] = target
                    match["batting"] = 1

                match["innings"] = 2

                return {
                    "status": "innings_end",
                    "target": target,
                    "score1": match["score1"],
                    "score2": match["score2"]
                }

            else:
                return {
                    "status": "match_end",
                    "score1": match["score1"],
                    "score2": match["score2"]
                }

        return {
            "status": "wicket",
            "choice1": choice1,
            "choice2": choice2,
            "score1": match["score1"],
            "score2": match["score2"],
            "wickets": wickets
        }

    # Batter gets their chosen number
    if match["batting"] == 1:
        match["score1"] += choice1
        current_score = match["score1"]
    else:
        match["score2"] += choice1
        current_score = match["score2"]

    # Second innings target reached
    if match["innings"] == 2 and match["target"] is not None:

        if current_score >= match["target"]:
            return {
                "status": "match_end",
                "winner": match["batting"],
                "score1": match["score1"],
                "score2": match["score2"]
            }

    return {
        "status": "runs",
        "runs": choice1,
        "choice1": choice1,
        "choice2": choice2,
        "score1": match["score1"],
        "score2": match["score2"]
    }
