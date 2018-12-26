from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
import time

class Player(object):
    def __init__(self, name):
        self.name = name
        self.id = self.get_id()
        self.headshot_url = self.get_headshot_url()
        self.fill_in_number_and_position()

    def get_id(self):
        players_with_matching_name = players.find_players_by_full_name(self.name)
        filtered_player_list = [player for player in players_with_matching_name if player['full_name'] == self.name]
        #print(filtered_player_list)
        player_info = filtered_player_list[0]
        return int(player_info['id'])

    def get_headshot_url(self):
        return "https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{}.png".format(self.id)

    def fill_in_number_and_position(self):
        print("Starting number/pos data retrieval for {}...".format(self.name))
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=self.id)
        print("Finished number/pos data retrieval...")
        common_info = player_info.common_player_info.get_dict()
        #print(common_info)
        jersey_num_ind = common_info['headers'].index('JERSEY')
        pos_ind = common_info['headers'].index('POSITION')
        jersey_num = common_info['data'][0][jersey_num_ind]
        position = common_info['data'][0][pos_ind]
        # jersey_num = 23
        # position = "SF"
        self.number = int(jersey_num)
        self.position = position
        time.sleep(0.25)