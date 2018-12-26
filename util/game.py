from bs4 import BeautifulSoup
import requests
import time

class Game(object):
    def __init__(self, team):
        self.link = self.get_game_link()
        #self.preferred_link = self.get_preferred_link()
        time.sleep(10)

    def get_game_link(self):
        return "https://www.reddit.com/r/nbastreams/comments/a8qdoo/game_thread_oklahoma_city_thunder_utah_jazz/"

    def get_preferred_link(self):
    	r = requests.get(self.link)
    	soup = BeautifulSoup(r.content)
    	print(soup)
    	preferred_link_str = soup.find(string="nba4live")
    	print(preferred_link_str)
    	print(preferred_link_str.find_parents("a"))
    	print(preferred_link_str)
    	return self.link