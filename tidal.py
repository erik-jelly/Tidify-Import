import oauth, creds

import time, requests, random, json
from pprint import pprint

API_URL = "https://openapi.tidal.com/v2"

def apiInteract(token, action, path=None, url=None, data=None, params=None):
    # if credentials["tokens"]["expiry"] - time.time() > 60:
    #     getTokens(clientid=credentials["client-id"], refreshToken=credentials["tokens"]["refreshToken"])

    if (path == None and url == None) or (path != None and url != None):
        raise ValueError("Specify only one of path or url")

    if path:
        url = API_URL + path
    
    header = {
        "accept" : "application/vnd.api+json",
        "Authorization": f"Bearer {token}"
    }

    for retry in range(6):
        if action == "get":
            response = requests.get(url, headers=header, params=params)
        elif action == "post":
            header["Content-Type"] = "application/vnd.api+json"
            response = requests.post(url, headers=header, json=data, params=params)

        if response.ok:
            return response
        else:
            if response.status_code == 429:
                ra = response.headers["Retry-After"]
                print(f"429 - Rate Limited - will retry in {ra}s.")
                time.sleep(float(ra) + random.random())
                continue
            else:
                error = {
                    "url" : url,
                    "header" : header,
                    "data" : data if data else None,
                    "status_code" : response.status_code,
                    "response" : response.json()
                }

                with open("errorlog.txt", "w") as f:
                    json.dump(error, f, indent=4)
        

    response.raise_for_status()

    return response

def createPlaylist(token, playlist):
    path = "/playlists"

    data = {
        "data": {
            "attributes": {
                "accessType": "PUBLIC" if playlist["public"] else "UNLISTED",
                "description": playlist["description"],
                "name": playlist["name"]
            },
            "type": "playlists"
        }
    }

    print(f"\tCreating playlist: {playlist["name"]}")
    response = apiInteract(token, "post", path=path, data=data)

    return response.json()["data"]["id"]

def findMatchingAlbum(responses, wantedAlbum):

    mostPopular = ["", 0]

    for response in responses:
        albums = {}
        for album in response.json()["included"]:
            albums[album["id"]] = {
                "name" : album["attributes"]["title"],
                "popularity" : album["attributes"]["popularity"]
            }

        for release in response.json()["data"]:
            if release["attributes"]["popularity"] > mostPopular[1]:
                mostPopular = [release["id"], release["attributes"]["popularity"]]
            for ref in release["relationships"]["albums"]["data"]:
                if albums[ref["id"]]["name"].casefold().strip() == wantedAlbum.casefold().strip():
                    return release["id"]

    return mostPopular[0]

def addSong(token, playlistid, song):
    if not song["isrc"]:
        print(f"\t\tSkipping {song["name"]} by {song["artists"]} - No ISRC")
        return

    path = "/tracks"

    params = {
        "countryCode" : "CA",
        "filter[isrc]" : song["isrc"].upper(),
        "include" : "albums"
    }

    responses = []

    response = apiInteract(token, "get", path=path, params=params)
    responses.append(response)

    while "next" in response.json()["links"]:
        response = apiInteract(token, "get", path=response.json()["links"]["next"])
        responses.append(response)

    if response.json()["data"]:
        path = f"/playlists/{playlistid}/relationships/items"

        if len(response.json()["data"]) > 1:
            id = findMatchingAlbum(responses, song["album"])
        else:
            id = response.json()["data"][0]["id"]

        data = {
            "data": [
                {
                "id": id,
                "type": "tracks"
                }
            ],
            "meta": {
                "onDuplicates": "SKIP",
            }
        }
        response = apiInteract(token, "post", path=path, data=data)
    else:
        print(f"\t\tCould not locate {song["name"]} by {song["artists"]} on Tidal using ISRC")

def findSong(token, isrc):

    path = "/tracks"

    params = {
        "countryCode" : "CA",
        "filter[isrc]" : isrc.upper(),
        "include" : "albums"
    }

    responses = []
    
    response = apiInteract(token, "get", path=path, params=params)
    responses.append(response)

    while "next" in response.json()["links"]:
        response = apiInteract(token, "get", path=response.json()["links"]["next"])
        responses.append(response)

    #pprint(response.json())

    return responses

def checkId(token, id):
    path = f"/tracks/{id}/relationships/albums"
    response = apiInteract(token, "get", path=path)
    pprint(response.json())

if __name__ == "__main__":
    credentials = creds.importCredentials()
    clientid = credentials["tidal"]["client-id"]
    tokens = credentials["tidal"]["tokens"]

    print("Authenticating User...", end="", flush=True)

    if tokens["expiry"] == None or tokens["expiry"] - time.time() < 60:
        if tokens["expiry"] == None:
            tokens = oauth.login(clientid, 1)
        else:
            tokens = oauth.getTokens(clientid=clientid, service=1, refreshToken=tokens["refreshToken"])
            if tokens == None:
                tokens = oauth.login(clientid, 1)
    
    credentials["tidal"]["tokens"] = tokens

    print(f"\r\033[K{"Authentication Complete"}")

    responses = findSong(tokens["accessToken"], "GBAHS2200039")
    pprint([response.json() for response in responses])
    pprint(findMatchingAlbum(responses, "CRASH"))
    # checkId(tokens["accessToken"], "408026341")

    # playlist = {"name" : "Test",
    #                 "href" : "",
    #                 "public" : False,
    #                 "description" : "This is a test, i really hope this works :)"}

    # createPlaylist(tokens["accessToken"], playlist)

    creds.exportCredentials(credentials)