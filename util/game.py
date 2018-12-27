from bs4 import BeautifulSoup
import requests
import time

class GameObject(object):
    def __init__(self, team):
        self.link = self.get_game_link()
        self.team = team
        self.preferred_link = self.get_preferred_link()
        #time.sleep(10)

    def get_game_link(self):
        return "http://nba4free.com/"

    def get_preferred_link(self):
    	r = requests.get(self.link)
    	soup = BeautifulSoup(r.content)
    	#print(soup)

        images = soup.findAll('img')
        for image in images:
            if self.team in image['src']:
                parent_tr = image.find_parents("tr")
                #print(parent_tr)
                game_links = parent_tr[len(parent_tr) / 2]
                #print(game_links)
                hd_link = game_links.find("a")['href']
                #print(hd_link)
                return hd_link
    	# preferred_link_str = soup.find(string=self.team)
    	# print(preferred_link_str)
    	# print(preferred_link_str.find_parents("td"))
    	#print(preferred_link_str)
    	return self.link