from bs4 import BeautifulSoup
import requests
import random
import wavelink
from typing import Literal
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from lib.utils.base_utils import get_config

def get_top100_artists_cache():
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
    return artists

top100_artists = get_top100_artists_cache()

async def get_top100_artists():
    return top100_artists

async def get_random_song():
    artists = await get_top100_artists()
    random_artist = random.choice(artists)

    tracks = await wavelink.Pool.fetch_tracks(f"spsearch:{random_artist}")
    track = random.choice(tracks)
    return track


async def song_from_artist(artist: str):
    artists = await get_top100_artists()
    
    # search
    for artist_it in artists:
        if str(artist_it) == artist:
            tracks = await wavelink.Pool.fetch_tracks(f"spsearch:{artist}")
            return random.choice(tracks[:15])
            
    return None


async def song_from_collection(top_num: int, from_best: bool = True, ret_tracks: bool = False):
    """
        `top_num` is the number of top artists (max 100)
        `from_best` if True will get top_num artists from the top, if False will fetch from the bottom of the list
    """
    artists = await get_top100_artists()
    
    if from_best:
        artist = random.choice(artists[:top_num])
        tracks = await wavelink.Pool.fetch_tracks(f"spsearch:{artist}")
        if ret_tracks: return tracks[:15]
        return random.choice(tracks[:15])

    artist = random.choice(artists[-(top_num-1):])
    tracks = await wavelink.Pool.fetch_tracks(f"spsearch:{artist}")
    return random.choice(tracks[:15])
    
async def many_songs_from_collection(num: int, top_num: int, from_best: bool = True):
    """Generate `num` unique songs with given criteria"""
    ret = []
    
    songs = await song_from_collection(top_num, from_best, ret_tracks=True)
    indices = []
    while not (len(indices) == num):
        rand = random.randint(0, num)
        if rand not in indices: indices.append(rand)
    
    for idx in indices:
        ret.append(songs[idx])
    return ret
    
async def many_songs_from_artist(artist: str, limit: str = 100):
    tracks = await wavelink.Pool.fetch_tracks(f"spsearch:{artist}")
    return tracks[:limit]

def new_songs_top1000():
    url = "https://b101.iheart.com/featured/bill-george/content/2023-01-03-the-top-1000-songs-of-all-time/"

    reqeust = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 5.0; rv:10.0) Gecko/20100101 Firefox/10.0",}).text

    soup = BeautifulSoup(reqeust, "html.parser")
    div = soup.find("div", {"class": "component-embed-html"})
    paragraphs = div.find_all("p")[1:]

    res = []

    for p in paragraphs:
        text = p.text
        num = text.split("\t", maxsplit=1)[0]
        if not num.isdigit(): continue
        res.append(text.split("\t", maxsplit=1)[1].replace("\t", " ").strip())
        
    return res
    
def fetch_2022_top100():
    url = "https://www.billboard.com/charts/year-end/hot-100-songs/"
    request = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 5.0; rv:10.0) Gecko/20100101 Firefox/10.0",}).text

    soup = BeautifulSoup(request, "html.parser")
    div = soup.find("div", {"class": "chart-results-list // u-padding-b-250"})
    divs = div.find_all("div", {"class": "o-chart-results-list-row-container"})
    
    parsed = []
    for elem in divs:
        inner = elem.find("ul", {"class": "o-chart-results-list-row"})
        text_elem = inner.find("li", {"class": "lrv-u-width-100p"}).find("ul").find("li", {"class": "o-chart-results-list__item"})
        title = text_elem.find("h3").get_text().strip()
        author = text_elem.find("span").get_text().strip()
        res = title + "-" + author
        parsed.append(res.strip())
    
    return parsed

songs = fetch_2022_top100()
cfg = get_config()["extensions"]["spotify"]
spotify_client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=cfg["client_id"], 
    client_secret=cfg["client_secret"]
))

async def random_songs_new(num: int, limit: int = 100):
    songs_collection = songs[:limit]
    ret = []
    indices = []
    while not (len(indices) == num):
        rand = random.randint(0, limit)
        if rand not in indices: indices.append(rand)
    
    # wavelink req    
    for idx in indices:
        track_url = spotify_client.search(songs_collection[idx], 1)["tracks"]["items"][0]["external_urls"]["spotify"]
        tracks = await wavelink.Pool.fetch_tracks(track_url)
        track = tracks[0]
        ret.append(track)
        
    return ret
