from bs4 import BeautifulSoup
from datetime import datetime
#from html.parser import HTMLParser
import html5lib
import requests
import time

r = requests.get("http://nba4free.com/")
#soup = BeautifulSoup(r.content,'html.parser')
soup = BeautifulSoup(r.content, 'html5lib')
#print(soup)

images = soup.findAll('img')
for image in images:
    #print image
    if 'suns' in image['src']:
        parent_tr = image.find_parent("tr")
        print(parent_tr)
        hd_link = parent_tr.find("a")['href']
        print(hd_link)