from bs4 import BeautifulSoup
import requests
import random
import wavelink
from typing import Literal

async def get_top100_artists():
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

async def get_random_song():
    artists = await get_top100_artists()

    random_artist = random.choice(artists)
    
    node: wavelink.Node = wavelink.NodePool.get_connected_node()
    tracks = await node.get_tracks(cls=wavelink.GenericTrack, query=f"ytsearch:{random_artist}")
    track = random.choice(tracks)
    return track


async def song_from_artist(artist: str):
    artists = await get_top100_artists()
    
    # search
    for artist_it in artists:
        if str(artist_it) == artist:
            node: wavelink.Node = wavelink.NodePool.get_connected_node()
            tracks = await node.get_tracks(cls=wavelink.GenericTrack, query=f"ytsearch:{artist}")
            return random.choice(tracks)
            
    return None


async def song_from_collection(top_num: int, from_best: bool = True):
    """
        `top_num` is the number of top artists (max 100)
        `from_best` if True will get top_num artists from the top, if False will fetch from the bottom of the list
    """
    artists = await get_top100_artists()
    
    if from_best:
        artist = random.choice(artists[:top_num])
        node: wavelink.Node = wavelink.NodePool.get_connected_node()
        tracks = await node.get_tracks(cls=wavelink.GenericTrack, query=f"ytsearch:{artist}")
        return random.choice(tracks)

    artist = random.choice(artists[-(top_num-1):])
    node: wavelink.Node = wavelink.NodePool.get_connected_node()
    tracks = await node.get_tracks(cls=wavelink.GenericTrack, query=f"ytsearch:{artist}")
    return random.choice(tracks)
    