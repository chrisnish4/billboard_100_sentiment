import requests 
import re
import genius_cred as gc
from urllib.parse import urlencode
from difflib import SequenceMatcher
from bs4 import BeautifulSoup

#client_id = gc.client_id
#client_secret = gc.client_secret
#access_token = gc.token

class GeniusAPI(object):
    
    def __init__(self, access_token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_token = access_token
        
    def similarity(self, string1, string2):
        """
        Returns similarty between strings (used to compare artist names)
        """
        sim = SequenceMatcher(None, string1, string2).ratio()
        return sim 
    
    def get_url(self, song, artist):
        access_token = self.access_token
        song = re.sub(r'[^\w\s]', '', song)
        song = song.replace(' ', '-')
        search_url = f"http://api.genius.com/search?q={song}&access_token={access_token}"
        response = requests.get(search_url)
        if response.status_code not in range(200,299):
            return {}
        json = response.json()
        
        url = None 
        for hit in json['response']['hits']: 
            search_artist = hit['result']['primary_artist']['name']
            if self.similarity(artist, search_artist)> 0.5 or artist[:5] in search_artist:
                url = hit['result']['url']
        
        return url
    
    def get_lyrics(self, song, artist):
        url = self.get_url(song, artist)
        if type(url) != str:
            return None
        lyrics = None 
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        html = soup.find('div', class_="Lyrics__Container-sc-1ynbvzw-6 YYrds")
        if html == None:
            return None
        lyrics = html.text
        
        return lyrics