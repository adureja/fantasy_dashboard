from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser, tz
import html5lib
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import commonplayerinfo, playerprofilev2
import requests
import time

NBA_ACTIVE_PLAYERS_URL = "https://data.nba.net/10s/prod/v1/2018/players.json"
NBA_BOXSCORE_URL = "http://data.nba.net/10s/prod/v1/{}".format(datetime.today().strftime('%Y%m%d')) + "/{}_boxscore.json"
NBA_TEAM_SCHEDULE_URL = "http://data.nba.net/10s/prod/v1/2018/teams/{}/schedule.json"
NBA_CURRENT_SCOREBOARD_URL = "http://data.nba.net/10s/prod/v1/{}/scoreboard.json".format(datetime.today().strftime('%Y%m%d'))


class PlayerObject(object):
    def __init__(self, name):
        self.name = name
        self.id = self.get_id()
        #self.team = self.get_team()
        self.headshot_url = self.get_headshot_url()
        self.fill_in_yearly_info()
        self.fill_in_next_game()

        ## To do:
        ## 1: Team ID, name? from commonPlayerInfo
        ## 2: Next game? from playerProfileV2
        ## 3: Averages: PTS REB AST 3Ps FGs FTs TO STL BLK MIN FL?

    ### NBA API CALLS

    def get_id(self):
        players_with_matching_name = players.find_players_by_full_name(self.name)
        filtered_player_list = [player for player in players_with_matching_name if player['full_name'] == self.name]
        #print(filtered_player_list)
        player_info = filtered_player_list[0]
        return int(player_info['id'])

    def get_headshot_url(self):
        return "https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{}.png".format(self.id)

    def retrieve_commonplayerinfo(self):
        print("Starting commonplayerinfo retrieval for {}...".format(self.name))
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=self.id)
        print("Finished commonplayerinfo data retrieval...")
        return player_info

    def retrieve_playerprofilev2(self):
        print("Starting playerprofilev2 data retrieval for {}...".format(self.name))
        player_profile = playerprofilev2.PlayerProfileV2(player_id=self.id, per_mode36="PerGame")
        print("Finished playerprofilev2 data retrieval...")
        return player_profile

    ### DATA.NBA.NET REQUEST CALLS
    def get_player_info(self):
        players = self.retrieve_active_players()
        player_info = next(iter(filter(lambda x: x.get('personId') == str(self.id), players)), None)
        return player_info

    def retrieve_active_players(self):
        return requests.get(NBA_ACTIVE_PLAYERS_URL).json().get('league').get('standard')

    def get_next_game(self):
        team_schedule = self.retrieve_team_schedule()
        next_game = next(iter(filter(lambda x: x.get('statusNum') == 1, team_schedule)), None)
        return next_game

    def retrieve_team_schedule(self):
        team_schedule_url = NBA_TEAM_SCHEDULE_URL.format(self.team_id)
        return requests.get(team_schedule_url).json().get('league').get('standard')


    # def fill_in_yearly_info(self):
    #     player_info = self.retrieve_commonplayerinfo()
    #     common_info = player_info.common_player_info.get_dict()
    #     # print(common_info)
    #     jersey_num_ind = common_info['headers'].index('JERSEY')
    #     pos_ind = common_info['headers'].index('POSITION')
    #     team_ind = common_info['headers'].index('TEAM_NAME')
    #     team_id_ind = common_info['headers'].index('TEAM_ID')

    #     jersey_num = common_info['data'][0][jersey_num_ind]
    #     position = common_info['data'][0][pos_ind]
    #     team = common_info['data'][0][team_ind]
    #     team_id = common_info['data'][0][team_id_ind]
    #     # jersey_num = 29
    #     # position = "SF"
    #     self.number = int(jersey_num)
    #     self.position = position
    #     self.team = team
    #     self.team_id = team_id

    #     time.sleep(5)

    def fill_in_yearly_info(self):
        player_info = self.get_player_info()

        self.number = player_info.get('jersey')
        self.position = player_info.get('pos')
        self.team_id = player_info.get('teamId')
        self.team = teams.find_team_name_by_id(self.team_id)['nickname']


    def fill_in_next_game(self):
        next_game_info = self.get_next_game()

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        
        _next_game_utc_datetime = parser.parse(next_game_info.get('startTimeUTC'))
        _next_game_utc_datetime.replace(tzinfo=from_zone)
        next_game_datetimeObj = _next_game_utc_datetime.astimezone(to_zone)
        
        self.next_game_date = next_game_datetimeObj.strftime('%b %d %Y').upper()
        self.next_game_time = next_game_datetimeObj.strftime('%I:%M %p')
        self.next_game_id = next_game_info.get('gameId')

    # def fill_in_next_game(self):
    #     player_profile = self.retrieve_playerprofilev2()
    #     next_game_info = player_profile.next_game.get_dict()

    #     game_date_ind = next_game_info['headers'].index('GAME_DATE')
    #     game_id_ind = next_game_info['headers'].index('GAME_ID')
    #     game_time_ind = next_game_info['headers'].index('GAME_TIME')

    #     game_date = next_game_info['data'][0][game_date_ind]
    #     game_id = next_game_info['data'][0][game_id_ind]
    #     game_time = next_game_info['data'][0][game_time_ind]

    #     self.next_game_date = game_date
    #     self.next_game_id = game_id
    #     self.next_game_time = game_time

    #     time.sleep(5)


