import urllib
from urllib.request import Request
import json
import http
from bs4 import BeautifulSoup

URL_BASE = "https://api.genius.com"
SEARCH_ENDPOINT = "/search?q="
TXT_FORMAT = "?text_format=plain"

class SearchResponse:
    """
    Converts a raw dictionary of search results (response from genius api) to a nice class

    Parameters
    ==================
    raw: `dict` - A raw dictionary of search results
    """
    def __init__(
        self,
        raw : dict,
    ):
        self.raw: dict = raw

        self.status: int = raw["meta"]["status"]
        self.response: dict = raw["response"]
        self.hits: list = raw["response"]["hits"]
        self.best_result: dict = self.hits[0]

        self.best_api_path: str = self.best_result["result"]["api_path"]
        self.best_id: int = self.best_result["result"]["id"]
        self.best_song_lang: str = self.best_result["result"]["language"]

class GeniusSong:
    def __init__(
        self, 
        raw: dict
    ):
        self.raw: dict = raw
        
        self.status: int = raw["meta"]["status"]
        self.response: dict = raw["response"]["song"]
        resp = self.response # to make life easier

        self.api_path: int = resp["api_path"]
        self.title: str = resp["full_title"]
        self.short_title: str = resp["title"]
        self.id: int = resp["id"]
        self.artist: str = resp["artist_names"]
        self.lang: str = resp["language"]
        self.description: str = resp["description"]["plain"]
        self.path: str = resp["path"]
        self.url: str = resp["url"]
        self.release_date: str = resp["release_date"]
        self.prettier_date: str = resp["release_date_for_display"]

        self.apple_music_id: None | int = resp.get("apple_music_id")
        self.apple_music_player_url: None | str = resp.get("apple_music_player_url")

        self.hedaer_img_url: str = resp["header_image_url"]
        self.header_thumbnail_url: str = resp["header_image_thumbnail_url"]
        self.song_art_thumb: str = resp["song_art_image_thumbnail_url"]
        self.song_art_img: str = resp["song_art_image_url"]

        self.lyrics_state: str = resp["lyrics_state"]

        self.stats: dict = resp["stats"]
        self.views: int = resp["stats"]["pageviews"]

    def __str__(self):
        return f"<GeniusSong> {self.short_title} by {self.artist} in lang: {self.lang} path: {self.path}"


def correct_string(string):
    "The string will be corrected so it can be used in an URL"
    return string.replace(" ", "%20")

class GeniusAPIClient():
    def __init__(self, genius_bearer_token: str):
        self._bearer: str = genius_bearer_token

    def _build_request(self, query: str, headers: dict=None) -> Request:
        query = correct_string(query)
        url = None
        if not headers:
            url, headers = self.get_request_data(query)
        url = url or query

        print(url)
        req: Request = Request(url=url, headers=headers)
        return req        
    
    def _fetch(self, request: Request, /, is_json: bool=False) -> http.client.HTTPResponse | dict:
        fetch = urllib.request.urlopen(request).read().decode('utf-8')

        if is_json:
            fetch = json.loads(fetch)

        return fetch

    def get_request_data(self, endpoint):
        """
        Get request data as an url and headers
        Returns a tuple
        
        Example of use:
            `url, headers = self.get_request_data(endpoint)`
        """
        url = URL_BASE + endpoint
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 5.0; rv:10.0) Gecko/20100101 Firefox/10.0",
            "Authorization": f"Bearer {self._bearer}"
        }
        return url, headers
    
    def search(self, query: str) -> SearchResponse:
        """
        Returns an object containing search results from Genius API
        """
        request = self._build_request(query = SEARCH_ENDPOINT + query)

        fetched_data = self._fetch(request, is_json=True)

        obj = SearchResponse(fetched_data)

        return obj

    def get_song(self, song: str) -> GeniusSong:
        """
        Get song informations from Genius API using `self.search()`. 
        Informations are extracted to a class to make life easier
        """
        data = self.search(song)
        song_endpoint = data.best_api_path

        request = self._build_request(song_endpoint + TXT_FORMAT)
        fetch = self._fetch(request, is_json=True)

        obj = GeniusSong(fetch)

        return obj
    
    def get_lyrics(self, lyrics_song_name: str) -> str:
        """
        Get lyrics using `self.get_song()`.
        Uses bs4 to scrape data from path fetched from function above
        """
        song = self.get_song(lyrics_song_name)
        path = song.url
        _, headers = self.get_request_data("")

        request = self._build_request(path, headers)
        fetched = self._fetch(request)

        soup = BeautifulSoup(fetched, "html.parser")
        found = soup.find("div", {"data-lyrics-container": True})
        
        found_parser = BeautifulSoup(str(found).replace("<br>", "<br/>").replace("<br/>", "\n"), "html.parser")

        return "".join(e for e in found_parser.strings)