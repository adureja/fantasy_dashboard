from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import commonplayerinfo, playerprofilev2

import time

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

    def fill_in_yearly_info(self):
        player_info = self.retrieve_commonplayerinfo()
        common_info = player_info.common_player_info.get_dict()
        # print(common_info)
        jersey_num_ind = common_info['headers'].index('JERSEY')
        pos_ind = common_info['headers'].index('POSITION')
        team_ind = common_info['headers'].index('TEAM_NAME')
        team_id_ind = common_info['headers'].index('TEAM_ID')

        jersey_num = common_info['data'][0][jersey_num_ind]
        position = common_info['data'][0][pos_ind]
        team = common_info['data'][0][team_ind]
        team_id = common_info['data'][0][team_id_ind]
        # jersey_num = 29
        # position = "SF"
        self.number = int(jersey_num)
        self.position = position
        self.team = team
        self.team_id = team_id

        time.sleep(5)

    def fill_in_next_game(self):
        player_profile = self.retrieve_playerprofilev2()
        next_game_info = player_profile.next_game.get_dict()

        game_date_ind = next_game_info['headers'].index('GAME_DATE')
        game_id_ind = next_game_info['headers'].index('GAME_ID')
        game_time_ind = next_game_info['headers'].index('GAME_TIME')

        game_date = next_game_info['data'][0][game_date_ind]
        game_id = next_game_info['data'][0][game_id_ind]
        game_time = next_game_info['data'][0][game_time_ind]

        self.next_game_date = game_date
        self.next_game_id = game_id
        self.next_game_time = game_time

        time.sleep(5)


