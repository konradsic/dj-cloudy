from bs4 import BeautifulSoup
import requests
import random

def get_random_song():
    artists = []
    
    req = requests.get("https://www.billboard.com/charts/artist-100/", headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 5.0; rv:10.0) Gecko/20100101 Firefox/10.0"
    })
    text = req.text
    soup = BeautifulSoup(text, "html.parser")

    table = soup.find("div", {"class":"chart-results-list"})
    
    elems = BeautifulSoup(str(table), "html.parser").find_all("div", {"class": "o-chart-results-list-row-container"})
    
    for elem in elems:
        indepth = elem.find("ul", {"class": "o-chart-results-list-row"}).find("li", {"class": "lrv-u-width-100p"}) \
            .find("ul", {"class": "lrv-a-unstyle-list"}).find("li", {"class": "o-chart-results-list__item"}).find("h3")
        artists.append(indepth.string.strip())

    random_artist = random.choice(artists)
    