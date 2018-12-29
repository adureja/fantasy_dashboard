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
