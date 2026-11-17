import oauth, creds

import time, requests
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

    if action == "get":
        response = requests.get(url, headers=header, params=params)
    elif action == "post":
        header["Content-Type"] = "application/vnd.api+json"
        response = requests.post(url, headers=header, json=data, params=params)

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

    response = apiInteract(token, "post", path=path, data=data)
    response.raise_for_status()

def addSong(token, song):
    path = "/tracks"

    params = {
        "countryCode" : "CA",
        "filter[isrc]" : song["isrc"]
    }

    response = apiInteract(token, "get", path=path, params=params)

    if response.json()["data"]:
        response = apiInteract(token, "post", path=path, params=params)
    else:
        print(f"Could not locate {song["name"]} on Tidal")


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

    playlist = {"name" : "Test",
                    "href" : "",
                    "public" : False,
                    "description" : "This is a test, i really hope this works :)"}

    createPlaylist(tokens["accessToken"], playlist)

    creds.exportCredentials(credentials)