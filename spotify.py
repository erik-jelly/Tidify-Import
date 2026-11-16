import oauth, creds

import time, requests
from pprint import pprint

import json

API_URL = "https://api.spotify.com/v1"

def apiGet(token, path = None, url = None, params = None):
    # if credentials["tokens"]["expiry"] - time.time() > 60:
    #     getTokens(clientid=credentials["client-id"], refreshToken=credentials["tokens"]["refreshToken"])

    if (path == None and url == None) or (path != None and url != None):
        raise ValueError("Specify only one of path or url")

    if path:
        url = API_URL + path
    
    header = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()

    return response

def getMyId(token):
    path = "/me"
    return apiGet(token, path=path).json()["id"]

def parsePlaylists(response, myid):
    playlists = []
    for playlist in response.json()["items"]:
        if playlist["owner"]["id"] == myid:
            playlists.append({
                "name" : playlist["name"],
                "href" : playlist["href"],
                "public" : playlist["public"],
                "collaborative" : playlist["collaborative"],
                "description" : playlist["description"],
            })

    return playlists

def getPlaylists(token):
    path = "/me/playlists"
    params = {
        "limit" : 20,
        "offset" : 0
    }

    myid = getMyId(token)

    response = apiGet(token, path=path, params=params)

    playlists = []

    playlists += parsePlaylists(response, myid)

    while response.json()["next"]:
        response = apiGet(token, url=response.json()["next"])
        playlists += parsePlaylists(response, myid)
        

    return playlists

def parseSongs(response):
    songs = []
    for song in response.json()["items"]:
        songs.append({
            "name" : song["item"]["name"],
            "artists" : [artist["name"] for artist in song["item"]["artists"]],
            "isrc" : song["item"]["external_ids"]["isrc"]
        })

    return songs

def getSongs(token, playlist):
    songs = []

    response = apiGet(token, url=f"{playlist["href"]}/items")

    songs += parseSongs(response)

    while response.json()["next"]:
        response = apiGet(token, url=response.json()["next"])
        response.raise_for_status()
        songs += parseSongs(response)

    return songs

if __name__ == "__main__":
    credentials = creds.importCredentials()
    clientid = credentials["spotify"]["client-id"]
    tokens = credentials["spotify"]["tokens"]

    print("Authenticating User...", end="", flush=True)

    if tokens["expiry"] == None or tokens["expiry"] - time.time() < 60:
        if tokens["expiry"] == None:
            tokens = oauth.login(clientid, 0)
        else:
            tokens = oauth.getTokens(clientid=clientid, refreshToken=tokens["refreshToken"])
            if tokens == None:
                tokens = oauth.login(clientid, 0)

    credentials["spotify"]["tokens"] = tokens

    print(f"\r\033[K{"Authentication Complete"}")
    #pprint(tokens)

    print("Getting Spotify Playlists...", end="", flush=True)

    playlists = getPlaylists(tokens["accessToken"])
    
    print(f"\r\033[K{"Spotify Playlists Retrieved!"}")

    songs = getSongs(tokens["accessToken"], playlists[1])

    pprint(songs)

    creds.exportCredentials(credentials)