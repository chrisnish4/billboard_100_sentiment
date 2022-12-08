## Most of this is from CodingEntrpreneurs on Youtube, 
### My original methods: get_song_id, get_popularity, get_audio_features

import requests 
import spotify_cred as sc # Spotify credentials
import base64
from urllib.parse import urlencode
import datetime as dt
from difflib import SequenceMatcher

client_id = sc.client_id
client_secret = sc.client_secret

class SpotifyAPI(object):
    access_token = None 
    access_token_expires = dt.datetime.now()
    access_token_did_expire = True
    client_id = None 
    client_secret = None 
    token_url = 'https://accounts.spotify.com/api/token'

    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs) ## calls any class it inherits from self 
        self.client_id = client_id
        self.client_secret = client_secret 
        
    def get_client_credentials(self):
        """
        Returns base 64 encoded string required for Spotify authentication
        """
        client_id = self.client_id
        client_secret = self.client_secret
        
        if client_id == None or client_secret == None:
            raise Exception("Client ID and Client Secret must be set.")
            
        client_cred = f'{client_id}:{client_secret}'
        b64_client_cred = base64.b64encode(client_cred.encode())
        return b64_client_cred.decode()
        
    def get_token_header(self):
        b64_client_cred = self.get_client_credentials()
        token_headers = {
            'Authorization': f"Basic {b64_client_cred}", 
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        return token_headers
    
    def get_token_data(self):
        token_data = {
            'grant_type': 'client_credentials'
        }
        return token_data
        
    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_header()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        
        if r.status_code not in range(200,299):
            return False
        
        token_response_data = r.json()
        now = dt.datetime.now()
        access_token = token_response_data['access_token']
        expires_in = token_response_data['expires_in']
        expires = now + dt.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True
    
    def get_access_token(self):
        auth_done = self.perform_auth
        if not auth_done:
            raise Exception("Authentication failed.")
        
        token = self.access_token 
        expires = self.access_token_expires
        now = dt.datetime.now()
        
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        
        return token 
    
    def get_track_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        } 
        return headers
    
    # not be necessary
    """
    def get_track(self, lookup_id):
        endpoint = f"https://api.spotify.com/v1/tracks/{lookup_id}"
        headers = self.get_track_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()
    """
    
    def get_song_id(self, song_name, artist_name):
        search_dict = self.search(song_name)
        song_id = None
        popularity = None
        
        track_items = search_dict['tracks']['items']
        for i in track_items:
            if artist_name[:5] in i['artists'][0]['name'] or SequenceMatcher(None, artist_name, i['artists'][0]['name']).ratio() >= 0.45:
                song_id = i['id']
                popularity = i['popularity']
            else:
                continue
        return song_id, popularity
    
    def get_popularity(self, song_name, artist_name):
        popularity = self.get_song_id(song_name, artist_name)[1]
        return popularity
    
    def get_audio_features(self, song_name, artist_name):
        song_id, popularity = self.get_song_id(song_name, artist_name)
        endpoint = f'https://api.spotify.com/v1/audio-features/{song_id}'
        headers = self.get_track_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()
    
    def search(self, query, search_type="track"):
        query = query.lower().replace(' ', '+')
        access_token = self.access_token
        endpoint = "https://api.spotify.com/v1/search"
        headers = self.get_track_header()
        
        data = urlencode({'q': query, 'type':search_type.lower()})
        lookup_url = f"{endpoint}?{data}"
        
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()