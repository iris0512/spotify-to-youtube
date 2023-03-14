import pandas as pd
import os
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from datetime import datetime
import configparser
import time

config = configparser.ConfigParser()
config.read('credentials.ini')
youtube = config['youtube']

#connecting to youtube
api_key = youtube['api_key']
api_service_name = 'youtube'
api_version = 'v3'
yt_base_url = 'https://www.googleapis.com/youtube/v3'
path = youtube['path']
client_secrets_file = youtube['client_secrets_file']


def connectYouTube(api_service_name,api_version,api_key):
    #populates the definitions for the api methods and functions being used
    #The discovery.build() method builds a service object (the resource variable) 
    #for the Google Python API client which allows to easily use built-in 
    #methods to access API endpoints for a given API 
    youtube = googleapiclient.discovery.build(api_service_name, 
                                         api_version, developerKey=api_key)
    return youtube

def accessTokenYoutube(client_secrets_file):
    #https://github.com/googleapis/google-api-python-client/blob/main/docs/oauth.md
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(host='localhost',
    port=8080, 
    authorization_prompt_message='Please visit this URL: {url}', 
    success_message='The auth flow is complete; you may close this window.',
    open_browser=True)
    youtube_oauth = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    return youtube_oauth


def createPlaylist(youtube,playlist_names):
    #playlist names extracted from spotify
    youtube_playlists = []
    for i in range(len(playlist_names)):
        request = youtube.playlists().insert(
            part="snippet",
            body={
              "snippet": {
              "title": playlist_names[i]
              }
            }
        )
        response = request.execute()
        #to check if request has been successful
        title = playlist_names[i]
        playlist_id = response["id"]
        youtube_playlists.append([title,playlist_id])
        print("Playlist ",playlist_names[i],"created with playlist id", response["id"])
        return youtube_playlists
    
def searchYouTube(youtube,playlist_items):
    try:
        for i in range(len(playlist_items)):
            name = playlist_items.iloc[i][1]
            album = playlist_items.iloc[i][2]
            artist = playlist_items.iloc[i][3]
            query = name+" "+album+" "+artist
            request = youtube.search().list(
                part="snippet",
                maxResults=1,
                q=query,
                type="video"
            )
            response = request.execute()
            if response:
                if response["items"]:
                    #concatenating with '' to preserve data integrity when saving data to excel
                    playlist_items.loc[i,'videoId'] = "'"+response["items"][0]["id"]["videoId"]+"'"
                else:
                    playlist_items.loc[i,'videoId'] = False
        return playlist_items,None
    except Exception as e:
        return playlist_items, e
    
#function to get the playlist IDs for youtube playlists
def getPlaylist(youtube):
    request = youtube.playlists().list(
        part="id,snippet",
        maxResults=50,
        mine=True
    )
    response = request.execute()
    youtube_playlists = []
    for i in range(len(response['items'])):
        title = response['items'][i]['snippet']['title']
        playlist_id = response['items'][i]['id']
        youtube_playlists.append([title,playlist_id])
    return youtube_playlists

def populatePlaylist(youtube_oauth,playlist_ids,youtube_add):
    names = list(playlist_ids['playlist_name'])
    print('List of available playlists:')
    for i in range(len(playlist_ids)):
        if playlist_ids.iloc[i][2]=='N':
            print(playlist_ids.iloc[i][0])
    name = input("Which playlist would you like to add to today?")
    logs = []
    populated = str(playlist_ids[playlist_ids['playlist_name']==name]['populated'][0])
    if name in names and populated=='N':
        counter = addPlaylistItems(youtube_oauth,youtube_add[youtube_add['playlist_name']==name],0,logs)
        if counter==len(youtube_add[youtube_add['playlist_name']==name]):
            playlist_ids.loc[playlist_ids['playlist_name']==name,'populated']='Y'
            names.remove(name)
    else:
        print('Check your input and choose a playlist from the displayed list only!!')
        return populatePlaylist(youtube_oauth,playlist_ids,youtube_add)
    return playlist_ids,counter

#to check if the song has already been added to the playlist 
def checkYouTube(youtube,playlistId):
    videoID = []
    request = youtube.playlistItems().list(
        part="snippet",
        maxResults = 100,
        playlistId=playlistId
    )
    response = request.execute()
    for i in range(len(response["items"])):
        videoID.append(response["items"][i]["snippet"]["resourceId"]['videoId'])
    return videoID


def addPlaylistItems(youtube_oauth,youtube_add,counter,logs):
    #due to the credit limitations on GCP, we are adding songs from a single playlist each time
    playlistID = youtube_add.iloc[counter]['playlist_ID']
    check = checkYouTube(youtube_oauth,playlistID)
    try:
        while counter<=len(youtube_add):
            videoID = youtube_add.iloc[counter]['videoId'][1:-1]
            name = youtube_add.iloc[counter]['name']
            playlist_name = youtube_add.iloc[counter]['playlist_name']
            print("Checking if song ",name," already exists")
            if videoID in check:
                print('Song already present')
                counter+=1
            else:
                print("Now adding ",name," to ",playlist_name)
                request = youtube_oauth.playlistItems().insert(
                    part="snippet",
                    body={
                      "snippet": {
                      "playlistId": playlistID, 
                    "resourceId": {
                  "kind": "youtube#video",
                  "videoId": videoID
                    }
                  }
                }
              )
                response = request.execute()
                if response:
                    print(name," added to playlist")
                    time.sleep(10)
                else:
                    print('oops')
                counter+=1
            if counter==len(youtube_add):
                return counter
    except googleapiclient.errors.HttpError as e:
        if e.error_details[0]["reason"] == "videoNotFound":
            print("Video not found.")
            logs.append([videoID,name])
            print(counter)
            addPlaylistItems(youtube,youtube_add,counter+1,logs)
    except Exception as e:
        print("Exception",e)
        return counter