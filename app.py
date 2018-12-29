import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from util.player import PlayerObject
from util.game import GameObject

from datetime import datetime

from rq import Queue
from rq.job import Job
from worker import conn

import time

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

q = Queue(connection=conn)
#q.empty()

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
    q.empty()
    start_redis_queue_for_players()
    #return "Welcome back {}!".format(name)
    players = get_players()
    games = {game.team: game.link for game in get_games()}
    return render_template('dashboard.html', players=players, games=games)

def get_games():
    queue_games()
    games = Game.query.filter_by(date=get_date_today())

    return games

def queue_games():
    teams = set([p.team.lower() for p in Player.query.filter_by(next_game_date=get_date_today())])
    for team in teams:
        print(team)
        add_game_to_db(team)

def add_game_to_db(name):
    # we need to add a call to add these to RQ
    job = q.enqueue_call(
        func="app.create_game_object", args=(name,), result_ttl=5000
    )
    print(job.get_id())

def create_game_object(team_name):
    game = GameObject(team_name)
    time.sleep(2)
    job = q.enqueue_call(
        func=create_game_object, args=(team_name,), result_ttl=5000
    )
    # save the results
    try:
        print(team_name)
        print(get_date_today())
        old_game_info = Game.query.filter(Game.team==team_name).filter(Game.date==get_date_today()).first()
        #newPlayer.last_updated = datetime.now()
        print(old_game_info)
        if old_game_info:
            print("theres something here")
            old_game_info.link = game.preferred_link
            old_game_info.last_updated = datetime.now()
        else:
            print("nothing here for {}. makin new".format(team_name))
            old_game_info = game_to_game_model(game)
            db.session.add(old_game_info)

        db.session.commit()
        return old_game_info
    except:
        errors = []
        errors.append("Unable to add game for {} to database.".format(team_name))
        return {"error": errors}


### PLAYER METHODS

def add_player_to_db(name):
    # we need to add a call to add these to RQ
    job = q.enqueue_call(
        func="app.create_player_object", args=(name,), result_ttl=5000
    )
    print(job.get_id())

def get_players():
    # return [PlayerObject(name) for name in get_player_names()]
    gd = datetime.today().strftime('%b %d %Y').upper()
    #return Player.query.filter_by(next_game_date=gd).all()
    return Player.query.order_by(Player.next_game_date.asc(),Player.next_game_time.asc())

def get_player_names():    
    currList = [
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
        'Noah Vonleh',
        'Kent Bazemore',
        'Trevor Ariza',
        'Paul Millsap',
        'Jarrett Allen',
        'Monte Morris'
    ]

    return currList

def start_redis_queue_for_players():
    q.empty()
    for name in get_player_names():
        add_player_to_db(name)
    # for name in get_player_names():
    #     job = q.enqueue_call(
    #         func="app.create_player_object", args=(name,), result_ttl=5000
    #     )
    #     print(job.get_id())

def create_player_object(name):
    player = PlayerObject(name)
    #time.sleep(5)
    # save the results
    job = q.enqueue_call(
        func=create_player_object, args=(name,), result_ttl=5000
    )
    print(job.get_id())
    try:
        oldPlayer = Player.query.filter_by(name=name).first()
        #newPlayer.last_updated = datetime.now()
        if oldPlayer:
            oldPlayer.nba_player_id = player.id
            oldPlayer.name = player.name
            oldPlayer.jersey_num = player.number
            oldPlayer.position = player.position
            oldPlayer.last_updated = datetime.now()
            oldPlayer.team = player.team
            oldPlayer.team_id = player.team_id
            oldPlayer.next_game_date = player.next_game_date
            oldPlayer.next_game_time = player.next_game_time
            oldPlayer.next_game_id = player.next_game_id
        else:
            newPlayer = player_to_player_model(player)
            db.session.add(newPlayer)

        db.session.commit()
        return oldPlayer.id
    except:
        errors = []
        errors.append("Unable to add item {} to database.".format(name))
        return {"error": errors}

### HELPER METHODS

@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        player = Player.query.filter_by(id=job.result).first()
        print(player)
        return player
    else:
        return "Nay!", 202

def player_to_player_model(player):
    return Player(
        nba_player_id = player.id,
        name = player.name,
        jersey_num = player.number,
        position = player.position,
        team = player.team,
        team_id = player.team_id,
        next_game_date = player.next_game_date,
        next_game_time = player.next_game_time,
        next_game_id = player.next_game_id
    )

def game_to_game_model(game):
    return Game(
        date = game.date,
        team = game.team,
        link = game.preferred_link
    )

@app.template_filter('has_game_today')
def has_game_today(game_date):
    return get_date_today()==game_date

def get_date_today():
    return datetime.today().strftime('%b %d %Y').upper()

if __name__ == "__main__":
    # app.run()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
