import uuid

from sqlalchemy import func

from fourthand1web.app import db


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String, default=lambda: str(uuid.uuid4()), unique=True)
    phase = db.Column(db.String)
    plays_per_quarter = db.Column(db.Integer)
    ydline = db.Column(db.Integer, default=0)
    down = db.Column(db.Integer, default=1)
    first_down_ydline = db.Column(db.Integer)
    playnum = db.Column(db.Integer, default=0)
    quarter = db.Column(db.Integer, default=1)
    
    teams = db.relationship("Team", backref="game", lazy=True)
    plays = db.relationship("PlaySelection", backref="game")
    history = db.relationship("PlayHistory", backref="game", lazy=True)

    def _get_team_mapping(self, attr):
        teams = [team for team in self.teams if getattr(team, attr)]
        if len(teams) > 1:
            raise Exception("Multiple true values found...")
        return teams.pop() if teams else None

    def _swap_team_attr(self, attr, team):
        other_team = [other for other in self.teams if other != team].pop()
        setattr(other_team, attr, False)
        if team:
            setattr(team, attr, True)

    @property
    def won_coin_toss(self):
        return self._get_team_mapping("won_coin_toss")

    @property
    def kicking(self):
        return self._get_team_mapping("kicking")

    @property
    def offense(self):
        return self._get_team_mapping("offense")

    @property
    def ball_carrier(self):
        return self._get_team_mapping("ball_carrier")

    @won_coin_toss.setter
    def won_coin_toss(self, team):
        self._swap_team_attr("won_coin_toss", team)

    @kicking.setter
    def kicking(self, team):
        self._swap_team_attr("kicking", team)

    @offense.setter
    def offense(self, team):
        self._swap_team_attr("offense", team)

    @ball_carrier.setter
    def ball_carrier(self, team):
        self._swap_team_attr("ball_carrier", team)

    @property
    def current_play(self):
        if self.plays:
            return max(self.plays, key=lambda play: play.playnum)
        else:
            return self.new_play()

    def update_current_offense_play(self, card_id, offset):
        self.current_play.offense_id = card_id
        self.current_play.offense_offset = offset if card_id else None
        db.session.commit()
    
    def update_current_defense_play(self, card_id, offset):
        self.current_play.defense_id = card_id
        self.current_play.defense_offset = offset if card_id else None
        db.session.commit()

    def new_play(self):
        new = PlaySelection(playnum=len(self.plays) + 1)
        self.plays.append(new)
        db.session.commit()
        return new

    @staticmethod
    def retrieve(public_id):
        return Game.query.filter_by(public_id=public_id).one()

    @staticmethod
    def save(**config):
        game_row = Game.create(**config)
        db.session.add(game_row)
        db.session.commit()
        return game_row

    @staticmethod
    def create(**config):
        return Game(plays_per_quarter=config["plays_per_quarter"])

    def add_team(self, team_row):
        self.teams.append(team_row)
        db.session.commit()


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    color = db.Column(db.String(6))
    score = db.Column(db.Integer, default=0)
    plays = db.relationship("PlayHistory", backref="ball_carrier", lazy=True)
    
    gameid = db.Column(db.Integer, db.ForeignKey("game.id"))

    won_coin_toss = db.Column(db.Boolean, default=False)
    ball_carrier = db.Column(db.Boolean, default=False)
    kicking = db.Column(db.Boolean, default=False)
    offense = db.Column(db.Boolean, default=False)

    __table_args__ = (db.UniqueConstraint("gameid", "name"), )

    @staticmethod
    def save(**config):
        team_row = Team.create(**config)
        db.session.add(team_row)
        db.session.commit()
        return team_row

    @staticmethod
    def create(**config):
        return Team(name=config["name"])


class PlaySelection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playnum = db.Column(db.Integer, nullable=False)
    offense_id = db.Column(db.String(36), default=None)
    offense_offset = db.Column(db.Integer, default=None)
    defense_id = db.Column(db.String(36), default=None)
    defense_offset = db.Column(db.Integer, default=None)

    gameid = db.Column(db.Integer, db.ForeignKey("game.id"))

    def is_ready(self):
        fields = [self.offense_id, self.offense_offset, self.defense_id, self.defense_offset]
        return all(val is not None for val in fields)



# Not a full recounting (that is, not the event list). Just what's needed to display the outcome.
class PlayHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_yd = db.Column(db.Integer)
    end_yd = db.Column(db.Integer)
    turnover = db.Column(db.Boolean)
    turnover_yd = db.Column(db.Integer)
    score = db.Column(db.Boolean)

    gameid = db.Column(db.Integer, db.ForeignKey("game.id"))
    teamid = db.Column(db.Integer, db.ForeignKey("team.id"))
