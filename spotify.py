import secrets, hashlib, base64
from urllib.parse import urlencode
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

import json

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "playlist-read-private"

def login():
    verifier = secrets.token_urlsafe(64);
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
    state = secrets.token_urlsafe(16)

    with open("./client-creds.json") as f:
        clientCreds = json.load(f)

    params = {
        "client_id" : clientCreds("client-id"),
        "response_type" : 'code',
        "redirect_uri" : REDIRECT_URI,
        "state" : state,
        "scope" : SCOPES,
        "code_challenge_method" : "S256",
        "code_challenge" : challenge
    }

    url = "https://accounts.spotify.com/authorize?" + urlencode(params)

    




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