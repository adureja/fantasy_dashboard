import app
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def sync_gamelog_data():
    print('Syncing gamelog data at {}'.format(datetime.now()))
    print("Getting players...")
    players = app.get_players()
    print("Syncing gamelogs for players...")
    app.queue_gamelogs(players)
    print('Sync complete.')

@sched.scheduled_job('cron', minutes='30')
def sync_players():
    print('Syncing player data at {}'.format(datetime.now()))
    print("Syncing players...")
    app.start_redis_queue_for_players()
    print("Synced players.")

@sched.scheduled_job('interval', minutes=5)
def sync_game_data():
    print("Syncing games... at {}".format(datetime.now()))
    app.queue_games()
    print("Syncing games complete.")

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')

sched.start()
