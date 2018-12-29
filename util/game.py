from bs4 import BeautifulSoup
from datetime import datetime
import html5lib
import requests
import time

class GameObject(object):
    def __init__(self, team):
        self.link = self.get_game_link()
        self.date = self.get_date_today()
        self.team = team
        self.preferred_link = self.get_preferred_link()
        #time.sleep(10)

    def get_date_today(self):
        return datetime.today().strftime('%b %d %Y').upper()

    def get_game_link(self):
        return "http://nba4free.com/"

    def get_preferred_link(self):
    	r = requests.get(self.link)
    	soup = BeautifulSoup(r.content, 'html5lib')
    	#print(soup)

        images = soup.findAll('img')
        for image in images:
            if self.team in image['src']:
                parent_tr = image.find_parent("tr")
                #print(parent_tr)
                hd_link = parent_tr.find("a")['href']
                #print(hd_link)
                return hd_link
    	# preferred_link_str = soup.find(string=self.team)
    	# print(preferred_link_str)
    	# print(preferred_link_str.find_parents("td"))
    	#print(preferred_link_str)
    	return self.link