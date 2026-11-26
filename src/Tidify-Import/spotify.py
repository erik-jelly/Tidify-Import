# Copyright (C) 2026 Erik Jelezarov (@erik-jelly)
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Tidify-Import, licensed under the GNU GPL v3 or later.
# See the LICENSE file in the project root for details.

import oauth, creds

import time, requests, random, json
from pprint import pprint

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

    for attempt in range(6):
        if response.ok:
            return response
        else:
            if response.status_code == 429:
                ra = float(response.headers["Retry-After"]) if response.headers["Retry-After"].isdigit() else min(2 ** attempt, 60)
                print(f"429 - Rate Limited - will retry in {ra}s.")
                time.sleep(ra + random.random())
                continue
            else:
                error = {
                    "url" : url,
                    "header" : header,
                    "status_code" : response.status_code,
                    "response" : response.json()
                }

                with open("errorlog.txt", "w") as f:
                    json.dump(error, f, indent=4)
        
    response.raise_for_status()

    return response

def getMyId(token):
    path = "/me"
    return apiGet(token, path=path).json()["id"]

def parsePlaylists(token, response, myid):
    playlists = []
    for playlist in response.json()["items"]:
        if playlist["owner"]["id"] == myid:
            print(f"\tFound Playlist: {playlist["name"]}")
            playlists.append({
                "name" : playlist["name"],
                "href" : playlist["href"],
                "public" : playlist["public"],
                "collaborative" : playlist["collaborative"],
                "description" : playlist["description"],
                "songs" : getSongs(token, playlist)
            })

    return playlists

def getPlaylists(token):
    path = "/me/playlists"
    params = {
        "limit" : 20,
        "offset" : 0
    }

    playlists = []

    myid = getMyId(token)

    response = apiGet(token, path=path, params=params)
    playlists += parsePlaylists(token, response, myid)

    while response.json()["next"]:
        response = apiGet(token, url=response.json()["next"])
        playlists += parsePlaylists(token, response, myid)

    print(f"\tTotal of {len(playlists)} playlists identified.")
    
    return playlists

def parseSongs(response):
    songs = []
    for song in response.json()["items"]:
        songs.append({
            "name" : song["item"]["name"],
            "album" : song["item"]["album"]["name"],
            "artists" : [artist["name"] for artist in song["item"]["artists"]],
            "isrc" : song["item"]["external_ids"]["isrc"] if "isrc" in song["item"]["external_ids"] else None
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
            tokens = oauth.getTokens(clientid=clientid, service=0, refreshToken=tokens["refreshToken"])
            if tokens == None:
                tokens = oauth.login(clientid, 0)

    credentials["spotify"]["tokens"] = tokens

    print(f"\r\033[K{"Authentication Complete"}")
    #pprint(tokens)

    print("Getting Spotify Playlists...")

    playlists = getPlaylists(tokens["accessToken"])

    pprint(playlists[1]["songs"])
    
    print(f"\r\033[K{"Spotify Playlists Retrieved!"}")

    creds.exportCredentials(credentials)