from fourthand1web import cards, models
from fourthand1web.app import socketio
from fourthand1.play import Play
from fourthand1web.utils import events_as_json, game_as_json, load_game_state, write_game_state


def _kick_action(game_id, action, event_name="kick-result"):
    game = load_game_state(models.Game.retrieve(game_id))
    events = getattr(game, action)()
    write_game_state(game_id, game)

    print([event.asjson() for event in events])
    
    payload = {
        "game": game_as_json(game),
        "events": events_as_json(events)
    }

    if event_name:
        socketio.emit(event_name, payload, to=game_id)

    return payload


def kickoff(game_id):
    return _kick_action(game_id, "kickoff")

def onside(game_id):
    return _kick_action(game_id, "onside")

def safety_punt(game_id):
    return _kick_action(game_id, "safety_punt")

def punt_in_bounds(game_id):
    return _kick_action(game_id, "punt_in_bounds")

def punt_out_of_bounds(game_id):
    return _kick_action(game_id, "punt_out_of_bounds")

def field_goal(game_id):
    return _kick_action(game_id, "field_goal")


def run_play(game_row):
    game = load_game_state(game_row)
    
    selection = game_row.current_play
    off_card = cards.get_offense_card(selection.offense_id)
    def_card = cards.get_defense_card(selection.defense_id)
    
    play = Play.create(off_card, def_card, selection.offense_offset, selection.defense_offset)
    events = game.play(play)
    print([event.asjson() for event in events])
    
    write_game_state(game_row.public_id, game)

    payload = {
        "game": game_as_json(game),
        "events": events_as_json(events),
        "offense": play.off_play.asjson(),
        "defense": play.def_play.asjson()
    }

    socketio.emit("play-result", payload)
    
    game_row.new_play()

    return payload
