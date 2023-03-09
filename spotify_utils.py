import spotipy
from spotipy import oauth2
import pandas as pd
import os
import requests
from datetime import datetime


#get the authorization code flow set up using spotipy package
#creates an oauth object and checks if token already exists 
#if it does not exist we get the authorization code and return new token
def spotifyConnect(client_id, client_secret,red_uri):
    scope = ['playlist-read-private','playlist-read-collaborative']
    
    sp_oauth = oauth2.SpotifyOAuth(client_id=client_id,
                                client_secret=client_secret,scope=scope,
                                redirect_uri=red_uri)

    access_token = ""

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


#gets user input to confirm which playlists to transfer to YT
def checkPlaylist(playlist_name):
    print("Do you want the playlist ",playlist_name," to be transferred?")
    playlist_transfer = input("Enter Y/N")[0]
    if playlist_transfer.upper() in ['Y','N']:
        playlist_status = playlist_transfer.upper()
        return playlist_status
    else:
        print("Check your input. Enter Y/N only")
        return checkPlaylist(playlist_name)


#returns all the playlist names that is created,liked 
#and followed by the user specified by the user id parameter
def getPlaylistNames(base_url,user_id,token):
    headers = {
    'Authorization': 'Bearer {}'.format(token)
    }
    #edit the limit option below appropriately
    playlist_endpoint = 'me/playlists?limit=50'
    playlist_endpoint_url = ''.join([base_url,playlist_endpoint])
    response = requests.get(playlist_endpoint_url,headers=headers)
    playlist_names = pd.DataFrame(columns = ['playlist_id','playlist_name','playlist_status'])
    #checking if the request returned a response successfully
    if response.status_code==200:
        playlist = response.json()
        playlist_title = []
        #iterating through the response to gather the playlist names and ids
        for i in range(len(playlist["items"])):
            playlist_name = playlist['items'][i]['name']
            playlist_id = playlist['items'][i]['id']
            playlist_status = checkPlaylist(playlist_name)
            playlist_title.append([playlist_id,playlist_name,playlist_status])
    else:
        return response.reason
    playlist_names = playlist_names.append(pd.DataFrame(playlist_title,
                                                          columns=['playlist_id','playlist_name','playlist_status']))
    return playlist_names


#get playlist items
def getPlaylistItems(base_url,playlist_names,token):
    headers = {
    'Authorization': 'Bearer {}'.format(token)
    }
    playlist_data = pd.DataFrame(columns = ['playlist_name','name','album','artist'])
    for i in range(len(playlist_names)):
        #sending requests only for playlists that have status as 'Y'
        if playlist_names.iloc[i][2]=='Y':
            print('Getting songs for the playlist ',playlist_names.iloc[i][1])
            #request to find the total length of the playlist
            playlist_total_endpoint = 'playlists/'+playlist_names.iloc[i][0]+'/tracks?fields=total,limit'
            playlist_total_endpoint_url = ''.join([base_url,playlist_total_endpoint])
            response_total = requests.get(playlist_total_endpoint_url,headers=headers)
            total = response_total.json()['total']
            limit = response_total.json()['limit']
            offset = 0
            batch = (total//limit)+1
            print("Number of songs in playlist:",total," and limit and batch are", limit,batch)
            playlist_details = []
            for j in range(1,batch+1):
                print('running batch',j)
                #request to get the playlist items based on limit and offset, 
                #since spotify by default only 100 songs in each request
                playlist_items_endpoint = 'playlists/'+playlist_names.iloc[i][0]+'/tracks?limit=100&offset='+str(offset)
                playlist_items_endpoint_url = ''.join([base_url,playlist_items_endpoint])
                response = requests.get(playlist_items_endpoint_url,headers=headers)
                playlist_items = response.json()
                #iterating through the playlist items response to get the track name, artist and album
                #we can also choose other information from the response object that can help with 
                #searching in YT
                for k in range(len(playlist_items['items'])):
                    track = playlist_items['items'][k]['track']['name']
                    album = playlist_items['items'][k]['track']['album']['name']
                    artist = playlist_items['items'][k]['track']['artists'][0]['name']
                    item = [playlist_names.iloc[i][1],track,album,artist]
                    playlist_details.append(item)
                #calculating the offset value
                offset = limit*j+1
                #checking if we have received all songs info
                if len(playlist_details)==total:
                    break
            print(len(playlist_details))
            playlist_data = playlist_data.append(pd.DataFrame(playlist_details,
                                                          columns=['playlist_name','name','album','artist']))
            print("Current size of playlist data",playlist_data.shape)
        else:
            print("Current playlist ",playlist_names.iloc[i][1]," not being considered.")
    return playlist_data