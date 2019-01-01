from bs4 import BeautifulSoup
from datetime import datetime
import html5lib
import requests
import time

NBA_BOXSCORE_URL = "http://data.nba.net/10s/prod/v1/{}".format(datetime.today().strftime('%Y%m%d')) + "/{}_boxscore.json"

class GamelogObject(object):
    def __init__(self, player_id, game_id):
        self.player_id = player_id
        self.game_id = game_id
        self.fill_in_box_score()
        #time.sleep(10)

    def fill_in_box_score(self):
        box_scores = self.fetch_box_score()
        #print(box_score)
        box_score = next(iter(filter(lambda x: x.get('personId') == self.player_id, box_scores.get('stats').get('activePlayers'))), None)
        basic_game_data = box_scores.get('basicGameData')
        #print(box_score)

        self.is_in_progress = basic_game_data.get('isGameActivated')
        self.is_on_court = box_score.get('isOnCourt')
        self.period_quarter_number = basic_game_data.get('period').get('current')
        self.period_minutes_left = basic_game_data.get('clock') if basic_game_data.get('clock') != "" else "00:00"
        self.points = box_score.get('points')
        self.minutes = box_score.get('min')
        self.fgm = box_score.get('fgm')
        self.fga = box_score.get('fga')
        self.ftm = box_score.get('ftm')
        self.fta = box_score.get('fta')
        self.tpm = box_score.get('tpm')
        self.tpa = box_score.get('tpa')
        self.rebounds = box_score.get('totReb')
        self.assists = box_score.get('assists')
        self.steals = box_score.get('steals')
        self.blocks = box_score.get('blocks')
        self.turnovers = box_score.get('turnovers')
        self.fouls = box_score.get('pFouls')

    def fetch_box_score(self):
        box_score_url = NBA_BOXSCORE_URL.format(self.game_id)
        print(box_score_url)
        return requests.get(box_score_url).json()

g = GamelogObject("2585", "0021800536")
print(vars(g))
# from datetime import datetime
# from dateutil import parser, tz
# from nba_api.stats.static import players, teams
# import requests
# import time

# NBA_ACTIVE_PLAYERS_URL = "https://data.nba.net/10s/prod/v1/2018/players.json"
# NBA_BOXSCORE_URL = "http://data.nba.net/10s/prod/v1/{}".format(datetime.today().strftime('%Y%m%d')) + "/{}_boxscore.json"
# NBA_TEAM_SCHEDULE_URL = "http://data.nba.net/10s/prod/v1/2018/teams/{}/schedule.json"
# NBA_CURRENT_SCOREBOARD_URL = "http://data.nba.net/10s/prod/v1/{}/scoreboard.json".format(datetime.today().strftime('%Y%m%d'))


# def show_active_players():
#     players = requests.get(NBA_ACTIVE_PLAYERS_URL).json().get('league').get('standard')
#     player_id = 2544
#     resource = next(iter(filter(lambda x: x.get('personId') == str(player_id), players)), None)
#     return resource

# def test_cpi():
#     player_info = show_active_players()

#     number = player_info.get('jersey')
#     position = player_info.get('pos')
#     team_id = player_info.get('teamId')
#     team = teams.find_team_name_by_id(team_id)['nickname']

#     print(number, position, team_id, team)

# def get_teams_next_game():
#     team_id = 1610612747
#     team_schedule_url = NBA_TEAM_SCHEDULE_URL.format(team_id)
#     print team_schedule_url
#     schedule = requests.get(team_schedule_url).json().get('league').get('standard')
#     resource = next(iter(filter(lambda x: x.get('statusNum') == 1, schedule)), None)
#     return resource

# def test_next_game():
#     next_game = get_teams_next_game()

#     from_zone = tz.tzutc()
#     to_zone = tz.tzlocal()
    
#     next_game_id = next_game.get('gameId')
#     _next_game_utc_datetime = parser.parse(next_game.get('startTimeUTC'))
#     _next_game_utc_datetime.replace(tzinfo=from_zone)
#     next_game_datetimeObj = _next_game_utc_datetime.astimezone(to_zone)
#     next_game_date = next_game_datetimeObj.strftime('%b %d %Y').upper()
#     next_game_time = next_game_datetimeObj.strftime('%I:%M %p')

#     print(next_game)

# def utc2local (utc):
#     epoch = time.mktime(utc.timetuple())
#     offset = datetime.fromtimestamp (epoch) - datetime.utcfromtimestamp (epoch)
#     return utc + offset

# if __name__ == '__main__':
#     # test_cpi()
#     test_next_game()