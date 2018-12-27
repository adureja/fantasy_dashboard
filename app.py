import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from util.player import PlayerObject
from util.game import GameObject


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import *

## Home Dashboard
@app.route('/')
def home():
    return "Fantasy Dashboard"

@app.route('/<name>')
def home_name(name):
    return "Welcome back {}!".format(name)

## Mission Control
@app.route('/dashboard')
def mission_control():
    return render_template('dashboard.html', players=get_players(), games=get_games())

def get_players():
    return [PlayerObject(name) for name in get_player_names()]

def get_games():
    return [GameObject("wizards")]

def get_player_names():    
    return [
        'John Wall', 
        'Russell Westbrook', 
        'Jrue Holiday',
        'Malcolm Brogdon',
        'Khris Middleton',
        'Bogdan Bogdanovic',
        'Paul George',
        'Pascal Siakam',
        'TJ Warren',
        'Rudy Gobert',
        'Jarrett Allen',
        'Kent Bazemore',
        'Trevor Ariza',
        'Paul Millsap'
    ]

## TODO: Player Cards

@app.route('/player_analyzer/<player_id>')
def player_card(player_id):
    return "This player's id is: {}".format(player_id)





if __name__ == "__main__":
    app.run()
