## spotify-to-youtube
---
to make transfer of playlists from spotify to youtube easier
##
##

### Table of Contents
---
- [Introduction](#introduction)
- [Requirements and Installation](#requirements-and-installation)
- [Spotify](#spotify)
- [YouTube](#youtube)
- [Future Improvements](#future-improvements)

### Introduction
---
This code is divided into two parts:
1. **Spotify**: This part connects to your spotify account and pulls all the playlists, created and followed. It then extracts the playlist items and stores it to a csv file which is then used as an input to the second part.
2. **YouTube**: This part reads the spotify data, creates playlists and adds songs to it.
### Requirements and Installation
---
1. Python - https://www.python.org/downloads/
2. Python extensions
    - google-auth-oauthlib
    - google-api-python-client
    - pandas
    - spotipy
3. Credentials for Spotify and Youtube
**Manual intervention needed to authenticate in browser or to create access token.**
### Spotify
---
 - Create an application at https://developer.spotify.com/dashboard
 - Update the `credentials.ini` file with the `client_id`, `client_secret `, `redirect_uri` and `user_id` under `[spotify]`.
  - Then run the `spotify_extraction.py` on the command line and follow the on-screen instructions to choose either to transfer all playlists or select playlists. 
 

### YouTube
---
- Create a Google Cloud Platform (GCP) project: https://console.cloud.google.com/apis/dashboard.
- Enable YouTube Data API and set up the OAuth credentials: https://developers.google.com/workspace/guides/configure-oauth-consent
    - Scopes: Add the scopes needed for the project or give general access to YouTube Data API v3 
    - Add test user for authentication purposes
    - The API Key can be created for use cases which does not need user private information, example: search function.
- Save the client secret file and API key and store the path in the `credentials.ini` file under `[youtube]` as  `CLIENT_SECRETS_FILE` and `API_KEY`.
- **Limitation**: Due to the credit limitations on GCP platform, we save all files as and when created, the code will need changes to read these files. 
- Run the `youtube_main.py` on the command line and follow on-screen instructions to complete transfer of playlists from Spotify to YouTube.
### Future Improvements
---
- For Spotify:
    - Allow user to transfer liked songs.
- For YouTube:
    - Add user interaction to allow for a menu of options to either go through entire process of creation of playlist, search and addition to playlist or just the required operation.
    - Check if playlist exists before creating. If it does ask whether to update or delete and create new one.
---

