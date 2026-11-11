import requests

clientid = ""
clientSecret = ""

def getAccessToken(id, secret):
    url = "https://accounts.spotify.com/api/token"
    header = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        # "client_id": id,
        # "client_secret": secret
    }
    auth = (id, secret)

    response = requests.post(url, headers=header, data=data, auth=auth)
    response.raise_for_status()
    print(response.json())
    token = response.json()["access_token"]

    return token

def getSpotifyPlaylists(accessToken):
    url = "https://api.spotify.com/v1/me/playlists"
    header = {"Authorization": f"Bearer {accessToken}"}

    response = requests.get(url, headers=header)
    response.raise_for_status()

    return response.json()

if __name__ == "__main__":
    token = getAccessToken(clientid, clientSecret)
    spotifyPlaylists = getSpotifyPlaylists(token)
    print(spotifyPlaylists)