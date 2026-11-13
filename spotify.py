import time

import secrets, hashlib, base64

from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser, requests

import json

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "playlist-read-private"

def createHTTPServer():
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsedURL = urlparse(self.path)

            if parsedURL.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Done! You can close this page now.")
            self.server.result = {k : v[0] for k, v in parse_qs(parsedURL.query).items()}

    server = HTTPServer(("127.0.0.1", 8888), RequestHandler)
    server.result = {}
    return server

def getTokens(codeVerifier, code, clientid):
    url = "https://accounts.spotify.com/api/token"
    header = {"Content-Type": "application/x-www-form-urlencoded"}
    body = {
        "grant_type" : "authorization_code",
        "code" : code,
        "redirect_uri" : REDIRECT_URI,
        "client_id" : clientid,
        "code_verifier" : codeVerifier
    }

    response = requests.post(url, headers=header, data=body)
    response.raise_for_status()

    tokens = {
        "accessToken" : response.json()["access_token"],
        "refreshToken" : response.json()["refresh_token"],
        "expiry" : time.time() + response.json()["expires_in"]
    }

    return tokens

def login():
    verifier = secrets.token_urlsafe(64);
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
    state = secrets.token_urlsafe(16)

    with open("client-creds.json", 'r') as f:
        clientCreds = json.load(f)

    params = {
        "client_id" : clientCreds["client-id"],
        "response_type" : 'code',
        "redirect_uri" : REDIRECT_URI,
        "state" : state,
        "scope" : SCOPES,
        "code_challenge_method" : "S256",
        "code_challenge" : challenge
    }

    url = "https://accounts.spotify.com/authorize?" + urlencode(params)

    server = createHTTPServer()
    server.timeout = 1
    
    webbrowser.open(url)
    deadline = time.time() + 180
    
    while not server.result and time.time() < deadline:
        server.handle_request()

    server.server_close()

    print(server.result)

    tokens = getTokens(verifier, server.result["code"], clientCreds["client-id"])
    print(tokens)

def getSpotifyPlaylists(accessToken):
    url = "https://api.spotify.com/v1/me/playlists"
    header = {"Authorization": f"Bearer {accessToken}"}

    response = requests.get(url, headers=header)
    response.raise_for_status()

    return response.json()

if __name__ == "__main__":
    login()