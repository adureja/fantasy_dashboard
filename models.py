from app import db
from sqlalchemy.dialects.postgresql import JSON


class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    nba_player_id = db.Column(db.Integer)
    name = db.Column(db.String())
    position = db.Column(db.String())
    
    
    def __init__(self, id, nba_player_id, name, position):
        self.id = id
        self.nba_player_id = nba_player_id
        self.name = name
        self.position = position

    def __repr__(self):
        return '<id {}>'.format(self.id)
