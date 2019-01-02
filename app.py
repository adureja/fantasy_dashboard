from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import logging
import os
import pytz
from random import shuffle
from rq import Queue
from rq.job import Job
import sys
from util.player import PlayerObject
from util.game import GameObject
from util.gamelog import GamelogObject
from worker import conn
import time

START_REDIS_QUEUE_FOR_DATA = False

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
db = SQLAlchemy(app)
# db.create_all()
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
def mission_control(queue_kickoff=START_REDIS_QUEUE_FOR_DATA):
    if queue_kickoff:
        print("Emptying redis queue...")
        q.empty()
        print("Starting redis queue for players...")
        start_redis_queue_for_players()
    #return "Welcome back {}!".format(name)
    print("Getting players...")
    players = get_players()
    print("Starting redis queue for games...")
    games = {game.team: game.link for game in get_games(queue_kickoff)}
    print("Rendering template for dashboard")
    gamelogs = get_gamelogs(players, queue_kickoff)
    return render_template('dashboard.html', players=players, games=games, gamelogs=gamelogs)

# def get_gamelogs(players):
#     print("Getting gamelogs lol")
#     players_today = [p for p in players if p.next_game_date == get_date_today()]
#     gamelogs = {}
#     for player in players_today:
#         gamelogs[player.nba_player_id] = GamelogObject(player.nba_player_id, player.next_game_id)
#     print(gamelogs)
#     return gamelogs

def get_gamelogs(players, queue_kickoff):
    if queue_kickoff:
        queue_gamelogs(players)
    #gamelogs = GameLog.query.filter(GameLog.last_created.time.date()==datetime.today().date())
    players_today = [p for p in players if p.next_game_date == get_date_today()]
    gamelogs = query_db_for_todays_gamelogs(players_today)
    gamelogs = {int(gamelog.player_id): gamelog for gamelog in gamelogs}
    # print(gamelogs)
    return gamelogs

def query_db_for_todays_gamelogs(players_today):
    gamelogs = [GameLog.query.filter(GameLog.game_id==p.next_game_id).filter(GameLog.player_id==str(p.nba_player_id)).first() for p in players_today]
    # gamelogs = GameLog.query.filter(GameLog.game_id.in_([p.next_game_id for p in players_today])).all()
    # print(gamelogs)
    return gamelogs

def queue_gamelogs(players):
    players_today = [p for p in players if p.next_game_date == get_date_today()]
    for player in players_today:
        # print(player.name)
        add_gamelog_to_db(player.nba_player_id, player.next_game_id)

def add_gamelog_to_db(player_id, game_id):
    # we need to add a call to add these to RQ
    job = q.enqueue_call(
        func="app.create_gamelog_object", args=(player_id, game_id, ), result_ttl=5000
    )
    print(job.get_id())

def create_gamelog_object(player_id, game_id):
    gamelog = GamelogObject(player_id, game_id)
    # time.sleep(2)
    # job = q.enqueue_call(
    #     func=create_gamelog_object, args=(player_id, game_id,), result_ttl=5000
    # )
    # save the results
    # print("created gamelog obj: {}".format(vars(gamelog)))
    try:
        #print(team_name)
        #print(get_date_today())
        old_gamelog = GameLog.query.filter(GameLog.player_id==str(player_id)).filter(GameLog.game_id==game_id).first()
        #newPlayer.last_updated = datetime.now()
        #print(old_gamelog)
        if old_gamelog:
            print("theres something here")
            #print(vars(game), vars(old_game_info))
            # print("curr old_gamelog: {}".format(vars(old_gamelog)))

            old_gamelog.is_in_progress = gamelog.is_in_progress
            old_gamelog.is_on_court = gamelog.is_on_court
            old_gamelog.period_quarter_number = gamelog.period_quarter_number
            old_gamelog.period_minutes_left = gamelog.period_minutes_left
            old_gamelog.points = gamelog.points
            old_gamelog.minutes = gamelog.minutes
            old_gamelog.fgm = gamelog.fgm
            old_gamelog.fga = gamelog.fga
            old_gamelog.ftm = gamelog.ftm
            old_gamelog.fta = gamelog.fta
            old_gamelog.tpm = gamelog.tpm
            old_gamelog.tpa = gamelog.tpa
            old_gamelog.rebounds = gamelog.rebounds
            old_gamelog.assists = gamelog.assists
            old_gamelog.steals = gamelog.steals
            old_gamelog.blocks = gamelog.blocks
            old_gamelog.turnovers = gamelog.turnovers
            old_gamelog.fouls = gamelog.fouls

            #db.session.commit()
            print("updated old_gamelog: {}".format(vars(old_gamelog)))
        else:
            print("nothing here for {}. makin new".format(player_id))
            old_gamelog = gamelog_to_gamelog_model(gamelog)
            db.session.add(old_gamelog)

        print("Committing to db")
        try:
            db.session.commit()
        except:
            db.session.rollback()
        print("Committed to db")
        return old_gamelog
    except:
        print('cant push gamelog')
        errors = []
        errors.append("Unable to add gamelog for {} to database.".format(player_id))
        return {"error": errors}

def get_games(queue_kickoff):
    clean_games_up()
    if queue_kickoff:
        queue_games()
    games = Game.query.filter_by(date=get_date_today())

    return games

def queue_games():
    teams = set([p.team.lower() for p in Player.query.filter_by(next_game_date=get_date_today())])
    for team in teams:
        # print(team)
        add_game_to_db(team)

def add_game_to_db(name):
    # we need to add a call to add these to RQ
    job = q.enqueue_call(
        func="app.create_game_object", args=(name,), result_ttl=5000
    )
    print(job.get_id())

def clean_games_up():
    old_games = Game.query.filter(~(Game.date==get_date_today())).all()
    for game in old_games:
        print('Deleting:{}'.format(game))
        db.session.delete(game)
    db.session.commit()

def create_game_object(team_name):
    game = GameObject(team_name)
    # time.sleep(2)
    # job = q.enqueue_call(
    #     func=create_game_object, args=(team_name,), result_ttl=5000
    # )
    # save the results
    try:
        #print(team_name)
        #print(get_date_today())
        old_game_info = Game.query.filter(Game.team==team_name).filter(Game.date==get_date_today()).first()
        #newPlayer.last_updated = datetime.now()
        print(old_game_info)
        if old_game_info:
            print("theres something here")
            #print(vars(game), vars(old_game_info))
            print("curr old_game_info: {}".format(vars(old_game_info)))
            old_game_info.link = game.preferred_link
            old_game_info.last_updated = datetime.now().replace(tzinfo=pytz.timezone('America/New_York'))
            #db.session.commit()
            print("updated old_game_info: {}".format(vars(old_game_info)))
        else:
            print("nothing here for {}. makin new".format(team_name))
            old_game_info = game_to_game_model(game)
            db.session.add(old_game_info)

        print("Committing to db")
        try:
            db.session.commit()
        except:
            db.session.rollback()
        print("Committed to db")
        return old_game_info
    except:
        print('cant')
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

def clean_players_up():
    players = Player.query.filter(~Player.name.in_(get_player_names())).all()
    for p in players:
        print(p.name)
        db.session.delete(p)
    db.session.commit()

def get_players():
    # return [PlayerObject(name) for name in get_player_names()]
    gd = datetime.today().strftime('%b %d %Y').upper()
    #return Player.query.filter_by(next_game_date=gd).all()
    return Player.query.order_by(Player.next_game_date.asc(),Player.next_game_time.asc()).all()

def get_player_names():    
    currList = [ 
        'Russell Westbrook', 
        'Jrue Holiday',
        'Malcolm Brogdon',
        'Khris Middleton',
        'Paul George',
        'Pascal Siakam',
        'TJ Warren',
        'Rudy Gobert',
        'Noah Vonleh',
        'Thaddeus Young',
        'Trevor Ariza',
        'Paul Millsap',
        'Otto Porter Jr.',
        'Gary Harris',
        'Nemanja Bjelica'
    ]

    shuffle(currList)

    return currList

def start_redis_queue_for_players():
    q.empty()
    clean_players_up()
    for name in get_player_names():
        add_player_to_db(name)
    # for name in get_player_names():
    #     job = q.enqueue_call(
    #         func="app.create_player_object", args=(name,), result_ttl=5000
    #     )
    #     print(job.get_id())

def create_player_object(name):
    currPlayer = PlayerObject(name)
    # print(vars(currPlayer))
    #time.sleep(5)

    # save the results
    # job = q.enqueue_call(
    #     func=create_player_object, args=(name,), result_ttl=5000
    # )
    print(job.get_id())
    try:
        print("Getting player from db for: {}".format(name))
        oldPlayer = Player.query.filter(Player.name==name).first()

        if oldPlayer:
            print("player exists in database:")
            oldPlayer.nba_player_id = currPlayer.id
            oldPlayer.name = currPlayer.name
            oldPlayer.jersey_num = currPlayer.number
            oldPlayer.position = currPlayer.position
            oldPlayer.last_updated = datetime.now()
            oldPlayer.team = currPlayer.team
            oldPlayer.team_id = currPlayer.team_id
            # print(datetime.now().time())
            # print(datetime.now().time().hour)
            # print(datetime.now().time().hour == int("12:00 PM"[:2]))
            # print(7 == )
            if (datetime.now().time().hour%12 <= int(oldPlayer.next_game_time[:2])):
                oldPlayer.next_game_date = currPlayer.next_game_date
                oldPlayer.next_game_time = currPlayer.next_game_time
                oldPlayer.next_game_id = currPlayer.next_game_id
            print("updated oldPlayer: {}".format(vars(oldPlayer)))
        else:
            print("new player being created in database:")
            newPlayer = player_to_player_model(currPlayer)
            print("converted playerobj to Player")
            db.session.add(newPlayer)

        print("Committing to db")
        db.session.commit()
        print("Committed to db")
        return oldPlayer.id
    except:
        print("ERROR IN PLAYER RETRIEVAL")
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

def gamelog_to_gamelog_model(gamelogObj):
    return GameLog(
        player_id = gamelogObj.player_id,
        game_id = gamelogObj.game_id,
        is_in_progress = gamelogObj.is_in_progress,
        is_on_court = gamelogObj.is_on_court,
        period_quarter_number = gamelogObj.period_quarter_number,
        period_minutes_left = gamelogObj.period_minutes_left,
        points = gamelogObj.points,
        minutes = gamelogObj.minutes,
        fgm = gamelogObj.fgm,
        fga = gamelogObj.fga,
        ftm = gamelogObj.ftm,
        fta = gamelogObj.fta,
        tpm = gamelogObj.tpm,
        tpa = gamelogObj.tpa,
        rebounds = gamelogObj.rebounds,
        assists = gamelogObj.assists,
        steals = gamelogObj.steals,
        blocks = gamelogObj.blocks,
        turnovers = gamelogObj.turnovers,
        fouls = gamelogObj.fouls
    )

@app.template_filter('get_statline')
def get_statline(gamelog):
    ## TODO: change arg to gamelog lol bc model shuld be passed in
    # gamelog = gamelog_to_gamelog_model(gamelog_model)
    if gamelog.minutes == "00:00":
        return "... has not played today."
    statline = "{} PTS, {} REB, {} AST, {} STL, {} BLK, {} TO".format(gamelog.points, gamelog.rebounds, gamelog.assists, gamelog.steals, gamelog.blocks, gamelog.turnovers)
    return statline

@app.template_filter('get_fantasy_pts')
def get_fantasy_pts(gamelog):
    ## TODO: change arg to gamelog lol bc model shuld be passed in
    # gamelog = gamelog_to_gamelog_model(gamelog_model)
    # print(vars(gamelog))
    total_pts = gamelog.points + gamelog.rebounds + gamelog.assists + gamelog.steals + gamelog.blocks - gamelog.turnovers
    return total_pts

@app.template_filter('has_game_today')
def has_game_today(game_date):
    return get_date_today()==game_date

def get_date_today():
    return datetime.today().strftime('%b %d %Y').upper()

if __name__ == "__main__":
    # app.run()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
