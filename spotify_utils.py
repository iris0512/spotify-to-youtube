#import spotipy
from spotipy import oauth2
import pandas as pd
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read('credentials.ini')
spotify = config['spotify']

#constant variables
client_id = spotify['client_id']
client_secret = spotify['client_secret']
user_id = spotify['user_id']
path = spotify['path']
#spotify base url
base_url = 'https://api.spotify.com/v1/'
#redirect url of your application
red_uri = spotify['redirect_uri']

#get the authorization code flow set up using spotipy package
#creates an oauth object and checks if token already exists 
#if it does not exist we get the authorization code and return new token
def getToken(client_id, client_secret,red_uri):
    scope = ['playlist-read-private','playlist-read-collaborative']
    
    sp_oauth = oauth2.SpotifyOAuth(client_id=client_id,client_secret=client_secret,scope=scope,
                                redirect_uri=red_uri)
    token_info = sp_oauth.get_cached_token()
    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        code = sp_oauth.get_authorization_code(response=None)
        if code:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    return access_token

def getPlaylists(sp):
    total = sp.current_user_playlists()["total"]
    limit = sp.current_user_playlists()["limit"]
    playlist = []
    offset = 0
    next = True
    while next:
        response = sp.current_user_playlists(offset=offset*limit)['items']
        for i in range(len(response)):
            name = response[i]['name']
            id = response[i]['id']
            playlist.append([name,id])
        offset+=1
        next = len(playlist) != total
    return playlist

def choosePlaylists(playlist):
    print('Do you want to transfer all playlists?')
    selection = input('Enter Y/N')[0].upper()
    if selection in ['Y','N']:
        if selection=='Y':
            playlist['transfer']='Y'
        else:
            print('Choose playlists for transfer')
            for i in range(len(playlist)):
                while True:
                    print('Playlist:',playlist.loc[i,'playlist_name'])
                    transfer = input('Enter Y/N')[0].upper()
                    if transfer=='Y':
                        playlist.loc[i,'transfer'] = 'Y'
                        break
                    elif transfer=='N':
                        playlist.loc[i,'transfer'] = 'N'
                        break
                    else:
                        print('Check your input!!')
                        continue                        
    return playlist

def playlistItems(sp,playlist):
    playlist_items = pd.DataFrame(columns = ['playlist_name','track','album','artist'])
    count = 0
    total_count = len(playlist[playlist['transfer']=='Y'])
    for i in range(len(playlist)):
        id = playlist.loc[i,'playlist_id']
        name = playlist.loc[i,'playlist_name']
        if playlist.loc[i,'transfer']=='Y':
            total = sp.playlist_items(id)["total"]
            limit = 100
            items = []
            offset = 0
            next = True
            while next:
                response = sp.playlist_items(id,offset=offset*limit)["items"]
                for j in range(len(response)):
                    track = response[j]['track']['name']
                    album = response[j]['track']['album']['name']
                    artist = response[j]['track']['artists'][0]['name']
                    items.append([name,track,album,artist])
                offset+=1
                next = len(items)!=total
            count+=1
            playlist_items = pd.concat([playlist_items,pd.DataFrame(items,columns = ['playlist_name','track','album','artist'])])
            print("Added",total,"tracks. Completed",count,"of",total,"playlists")
    return playlist_items