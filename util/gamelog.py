from bs4 import BeautifulSoup
from datetime import datetime
import html5lib
import requests
import time

NBA_BOXSCORE_URL = "http://data.nba.net/10s/prod/v1/{}".format(datetime.today().strftime('%Y%m%d')) + "/{}_boxscore.json"

class GamelogObject(object):
    def __init__(self, player_id, game_id):
        self.player_id = str(player_id)
        self.game_id = str(game_id)
        self.fill_in_box_score()
        #time.sleep(10)

    def fill_in_box_score(self):
        box_scores = self.fetch_box_score()
        basic_game_data = box_scores.get('basicGameData')
        
        self.is_in_progress = basic_game_data.get('isGameActivated')
        self.period_quarter_number = basic_game_data.get('period').get('current')
        self.period_minutes_left = basic_game_data.get('clock') if basic_game_data.get('clock') != ("" or "0:00") else "00:00"
        
        if box_scores.get('stats') and box_scores.get('stats').get('activePlayers'):
            active_players_box_scores = box_scores.get('stats').get('activePlayers')
            box_score = next(iter(filter(lambda x: x.get('personId') == self.player_id, active_players_box_scores)), None)
            #print(box_score)

            self.is_on_court = box_score.get('isOnCourt')
            self.points = int(box_score.get('points'))
            self.minutes = box_score.get('min')
            self.fgm = int(box_score.get('fgm'))
            self.fga = int(box_score.get('fga'))
            self.ftm = int(box_score.get('ftm'))
            self.fta = int(box_score.get('fta'))
            self.tpm = int(box_score.get('tpm'))
            self.tpa = int(box_score.get('tpa'))
            self.rebounds = int(box_score.get('totReb'))
            self.assists = int(box_score.get('assists'))
            self.steals = int(box_score.get('steals'))
            self.blocks = int(box_score.get('blocks'))
            self.turnovers = int(box_score.get('turnovers'))
            self.fouls = int(box_score.get('pFouls'))
        else:
            self.is_on_court = False
            self.points = 0
            self.minutes = "00:00"
            self.fgm = 0
            self.fga = 0
            self.ftm = 0
            self.fta = 0
            self.tpm = 0
            self.tpa = 0
            self.rebounds = 0
            self.assists = 0
            self.steals = 0
            self.blocks = 0
            self.turnovers = 0
            self.fouls = 0

    def fetch_box_score(self):
        box_score_url = NBA_BOXSCORE_URL.format(self.game_id)
        print(box_score_url)
        return requests.get(box_score_url).json()