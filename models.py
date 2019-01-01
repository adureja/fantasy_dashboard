from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    nba_player_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String())
    jersey_num = db.Column(db.Integer)
    position = db.Column(db.String())
    pts = db.Column(db.Float)
    last_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    team = db.Column(db.String())
    team_id = db.Column(db.Integer)
    next_game_date = db.Column(db.String(), nullable=True)
    next_game_id = db.Column(db.String(), nullable=True)
    next_game_time = db.Column(db.String(), nullable=True)
    
    def __init__(self, nba_player_id, name, jersey_num, position, team, team_id, next_game_date, next_game_id, next_game_time):
        self.nba_player_id = nba_player_id
        self.name = name
        self.jersey_num = jersey_num
        self.position = position
        self.team = team
        self.team_id = team_id
        self.next_game_date = next_game_date
        self.next_game_time = next_game_time
        self.next_game_id = next_game_id

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Game(db.Model):
    __tablename__ = 'games'

    date = db.Column(db.String(), primary_key=True)
    team = db.Column(db.String(), primary_key=True)
    link = db.Column(db.String())
    last_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, date, team, link):
        self.date = date
        self.team = team
        self.link = link

    def __repr__(self):
        return '<id {}-{}>'.format(self.team, self.date)

class GameLog(db.Model):
    __tablename__ = 'gamelogs'

    player_id = db.Column(db.String(), primary_key=True)
    game_id = db.Column(db.String(), primary_key=True)
    is_in_progress = db.Column(db.Boolean, default=False)
    is_on_court = db.Column(db.Boolean, default=False)
    period_quarter_number = db.Column(db.Integer, default=0)
    period_minutes_left = db.Column(db.String(), default="00:00")
    points = db.Column(db.Integer, default=0)
    minutes = db.Column(db.String(), default="00:00")
    fgm = db.Column(db.Integer, default=0)
    fga = db.Column(db.Integer, default=0)
    ftm = db.Column(db.Integer, default=0)
    fta = db.Column(db.Integer, default=0)
    tpm = db.Column(db.Integer, default=0)
    tpa = db.Column(db.Integer, default=0)
    rebounds = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    steals = db.Column(db.Integer, default=0)
    blocks = db.Column(db.Integer, default=0)
    turnovers = db.Column(db.Integer, default=0)
    fouls = db.Column(db.Integer, default=0)

    last_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, player_id, game_id, is_in_progress, is_on_court, period_quarter_number, period_minutes_left, points, minutes, fgm, fga, ftm, fta, tpm, tpa, rebounds, assists, blocks, steals, turnovers, fouls):
        self.player_id = player_id
        self.game_id = game_id
        self.is_in_progress = is_in_progress
        self.is_on_court = is_on_court
        self.period_quarter_number = period_quarter_number
        self.period_minutes_left = period_minutes_left
        self.points = points
        self.minutes = minutes
        self.fgm = fgm
        self.fga = fga
        self.ftm = ftm
        self.fta = fta
        self.tpm = tpm
        self.tpa = tpa
        self.rebounds = rebounds
        self.assists = assists
        self.steals = steals
        self.blocks = blocks
        self.turnovers = turnovers
        self.fouls = fouls

    def __repr__(self):
        return '<id {}-{}>'.format(self.player_id, self.game_id)
