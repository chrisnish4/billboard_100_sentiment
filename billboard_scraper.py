import requests
from bs4 import BeautifulSoup
import numpy as np

class BillboardScrape(object): 
    base_url = "https://www.billboard.com/charts/year-end/{}/hot-100-songs/"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def get_year(self, year):
        year_col = None
        if year in (2011,2016):
            year_col = np.zeros(99)+year
        else: 
            year_col = np.zeros(100)+year
        
        return year_col
        
    def get_songs(self, year):
        song_list = []
        base_url = self.base_url
        
        page = requests.get(base_url.format(year))
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all(id="title-of-a-story")
        
        if year in (2011, 2016):
            for i in results[:99]:
                song_name = i.text.replace('\n', '').replace('\t','')
                song_list.append(song_name)
        else:
            for i in results[:100]:
                song_name = i.text.replace('\n', '').replace('\t','')
                song_list.append(song_name)

        return song_list
        
    def get_artists(self, year):
        base_url = self.base_url
        
        page = requests.get(base_url.format(year))
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all('span', class_='c-label')
        
        artist_list = [results[i].text.replace('\n', '').replace('\t','') for i in range(1, len(results)+1, 2)]
        return artist_list
    
    def get_song_artist(self, year):
        year_col = self.get_year(year)
        songs = self.get_songs(year)
        artists = self.get_artists(year)
        info_dict = {"year": year,
                     "song": songs, 
                     "artist": artists}
        
        return info_dict