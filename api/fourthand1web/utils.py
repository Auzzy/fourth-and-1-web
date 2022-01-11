from fourthand1.game import Game, Team

from fourthand1web import models

def load_game_state(game_row):
    teams_list = [load_team_state(team) for team in game_row.teams]
    teams = {team.name: team for team in teams_list}
    game = Game(teams_list[0], teams_list[1], game_row.plays_per_quarter)
    
    game.ball_carrier = teams[game_row.ball_carrier.name] if game_row.ball_carrier else None
    game.kicking = teams[game_row.kicking.name] if game_row.kicking else None
    game.offense = teams[game_row.offense.name] if game_row.offense else None
    game.ydline = game_row.ydline
    game.down = game_row.down
    game.first_down_ydline = game_row.first_down_ydline
    game._playnum = game_row.playnum
    game._quarter = game_row.quarter
    game._phase = game_row.phase

    return game

def load_team_state(team_row):
    team = Team(team_row.name)
    team.score = team_row.score
    return team

def write_game_state(game_id, game):
    game_row = models.Game.retrieve(game_id)
    teams = {team.name: team for team in game_row.teams}
    
    game_row.ydline = game.ydline
    game_row.down = game.down
    game_row.first_down_ydline = game.first_down_ydline
    game_row.playnum = game._playnum
    game_row.quarter = game._quarter
    game_row.phase = game.phase
    
    game_row.ball_carrier = teams[game.ball_carrier.name] if game.ball_carrier else None
    game_row.kicking = teams[game.kicking.name] if game.kicking else None
    game_row.offense = teams[game.offense.name] if game.offense else None
    if game_row.won_coin_toss is None:
        game_row.won_coin_toss = game_row.ball_carrier

    models.db.session.commit()

    write_team_state(game_id, game)

def write_team_state(game_id, game):
    team1_row = models.Team.query.filter_by(gameid=game_id, name=game.team1.name)
    team1_row.score = game.team1.score

    team2_row = models.Team.query.filter_by(gameid=game_id, name=game.team1.name)
    team2_row.score = game.team2.score

    models.db.session.commit()

def team_as_json(team):
    if not team:
        return None
    return {"name": team.name, "score": team.score}

def game_as_json(game):
    return {
        "phase": game.phase,
        "actions": tuple(action for action in game.actions if action["name"] != "play"),
        "playsPerQuarter": game.plays_per_quarter,
        "kicking": team_as_json(game.kicking),
        "receiving": team_as_json(game.receiving),
        "offense": team_as_json(game.offense),
        "defense": team_as_json(game.defense),
        "ydline": game.ydline,
        "down": game.down,
        "firstDownYdline": game.first_down_ydline,
        "playnum": game._playnum,
        "quarter": game._quarter,
        "teams": [team_as_json(team) for team in (game.team1, game.team2)]
    }

def events_as_json(events):
    return [str(event) for event in events]
