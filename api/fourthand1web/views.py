import importlib.resources
import json
import os

from flask import request
from flask_socketio import join_room, leave_room

import fourthand1

from fourthand1web import actions, models
from fourthand1web.app import app, socketio
from fourthand1web.cards import get_all_defense_cards, get_all_offense_cards
from fourthand1web.utils import events_as_json, game_as_json, load_game_state, write_game_state



@app.route("/plays/offense")
def offense_plays():
    return {"cards": [card.asjson() for card in get_all_offense_cards()]}

@app.route("/plays/defense")
def defense_plays():
    return {"cards": [card.asjson() for card in get_all_defense_cards()]}


@app.route("/game/create", methods=["POST"])
def create_game():
    game = models.Game.save(plays_per_quarter=request.json["playsperquarter"])
    return {"gameid": game.public_id}

@app.route("/game/<game_id>/team/create", methods=["POST"])
def create_team(game_id):
    game_row = models.Game.retrieve(game_id)
    if len(game_row.teams) < 2:
        team_row = models.Team.save(name=request.json["name"])
        game_row.add_team(team_row)

        if len(game_row.teams) == 2:
            game = load_game_state(game_row)
            if game_row.won_coin_toss is None:
                game.coin_flip()
                write_game_state(game_id, game)

            socketio.emit("game-ready", game_as_json(game), to=game_id)

        return {"team": team_row.name}
    else:
        return {"error": "Too many teams."}, 400

@app.route("/game/<game_id>/load")
def load_game(game_id):
    game_row = models.Game.retrieve(game_id)
    game = load_game_state(game_row)

    return {"game": game_as_json(game)}


@app.route("/game/<game_id>/play/select-offense", methods=["POST"])
def select_offense_play(game_id):
    game_row = models.Game.retrieve(game_id)
    game = load_game_state(game_row)
    if "play" in game.action_names:
        game_row.update_current_offense_play(request.json.get("cardId"), request.json.get("offset"))
        if game_row.current_play.is_ready():
            return actions.run_play(game_row)
        return {}
    return {}, 400

@app.route("/game/<game_id>/play/select-defense", methods=["POST"])
def select_defense_play(game_id):
    game_row = models.Game.retrieve(game_id)
    game = load_game_state(game_row)
    if "play" in game.action_names:
        game_row.update_current_defense_play(request.json.get("cardId"), request.json.get("offset"))
        if game_row.current_play.is_ready():
            return actions.run_play(game_row)
        return {}
    return {}, 400

@app.route("/game/<game_id>/action", methods=["POST"], defaults={"action": None})
@app.route("/game/<game_id>/action/<action>", methods=["POST"])
def perform_action(game_id, action):
    action_name = action or request.json.get("action")
    if action_name:
        game_row = models.Game.retrieve(game_id)
        game = load_game_state(game_row)
        if action_name != "play" and action_name in game.action_names:
            return getattr(actions, action_name)(game_id)

    return {}, 400


@socketio.on('join')
def on_join(data):
    gameId = data["gameId"]
    join_room(gameId)

@socketio.on('leave')
def on_leave(data):
    gameId = data["gameId"]
    leave_room(gameId)
