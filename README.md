# Tidify Import

Tidify Import is used to export all your user created playlists in Spotify and import them into Tidal.

⚠️ This is still a work in progress, so there may still be some bugs. ⚠️

The program will let you know about any songs it was not able to find. These songs may exist in Tidal's catalog, so you will want to check and add them manually if they do exist. There are plans to improve the import algorithm in the future.


## Setup

1. Make sure Python is installed (built on Python 3.14)
2. Make sure the Requests module is installed

    `$ pip install requests`

3. Clone the repo
4. Rename `credentials.sample.json` to `credentials.json`
5. Setup Spotify and Tidal Web API Apps

    Both the Spotify and Tidal setup is very similar.

    ### Spotify API Setup

    1. Go to https://developer.spotify.com/dashboard and login.
    2. Read and accept the Developer terms of service.
    3. On the dashboard, click on the "Create app" button.
    4. Provide the info in the appropriate fields:
        
        * App Name: `Whatever you want`
        * Description: `Whatever you want`
        * Redirect URI: `http://127.0.0.1:8888/callback`
        * Which APIs?: `Check Web API`
    
    5. Check I agree to the terms... and click Save
    6. Copy your Client ID into the appropriate spot in `credentials.json`

    ### Tidal API Setup

    1. Go to https://developer.tidal.com/dashboard and login.
    2. Read and accept the Developer terms of service.
    3. On the dashboard, click on the "Create New App" button.
    4. Name your app whatever you want and click "Create App".
    5. Go to the settings tab.
    6. Click the Edit button.
    7. Under Oauth > Redirect URI 1 put `http://127.0.0.1:8888/callback`
    8. Under Scopes check `playlists.write`
    9. Click Save
    10. Copy your Client ID into the appropriate spot in `credentials.json`

# Running the Program
Change directories into the repo folder and it's as simple as one command:

  `python3 main.py`

On the first run you will see login pages for Spotify and Tidal throughout the process. Login and allow access.

## Authors

- [@erik-jelly](https://www.github.com/erik-jelly)

