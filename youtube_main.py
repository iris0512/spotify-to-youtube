import pandas as pd
import os
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from datetime import datetime
import configparser
from youtube_utils import *


#connecting to youtube using API key
youtube_api = connectYouTube(api_service_name,api_version,api_key)
#connecting to youtube using oauth client
youtube_oauth = accessTokenYoutube(client_secrets_file)
playlist_items = pd.read_csv(path+'playlist_items.csv')
playlist_names = playlist_items['playlist_name'].unique()

#creating youtube playlist
playlist_ids = createPlaylist(youtube_oauth,playlist_names)

#storing playlist ids for future runs 
#(due to credit limitations)
playlist_ids = pd.DataFrame(playlist_ids,columns=['playlist_name',
                                   'playlist_ID'])
playlist_ids.to_csv(path+'youtube_ids.csv',index=False)

playlist_ids = pd.read_csv(path+'youtube_ids.csv')

#prepping dataframe for searching songs on youtube
playlist_items['videoId'] = None

playlist_updated,e = searchYouTube(youtube_oauth,playlist_items)

playlist_with_video = playlist_updated[~playlist_updated['videoId'].isna()]
playlist_without_video = playlist_updated[playlist_updated['videoId'].isna()]

withvideo = 'playlist_items_with_video'+datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")+'.csv'
withoutvideo = 'playlist_items_without_video'+datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")+'.csv'
playlist_with_video.to_csv(path+withvideo,index=False,mode='a')
playlist_without_video.to_csv(path+withoutvideo,index=False,mode='a')

playlist_ids['populated'] = 'N'
youtube_add = playlist_with_video.merge(playlist_ids)
playlist_ids,counter = populatePlaylist(youtube_oauth,playlist_ids,youtube_add)
