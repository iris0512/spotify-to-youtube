from spotify_utils import *
import configparser
import spotipy

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
#connecting to spotify
token = getToken(client_id,client_secret,red_uri)

sp = spotipy.Spotify(auth=token)

playlist = getPlaylists(sp)
playlist = pd.DataFrame(playlist,columns=['playlist_name','playlist_id'])
playlist.to_csv(path+'playlist_names.csv',index=False)

playlist_chosen = choosePlaylists(playlist)
playlist_items = playlistItems(sp,playlist_chosen)
#storing playlist 
playlist_items.to_csv(path+'playlist_items.csv',index=False)
print('Data stored for further processing!')