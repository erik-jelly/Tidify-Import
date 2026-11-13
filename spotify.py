import time, sys, secrets, hashlib, base64, webbrowser, requests
from pprint import pprint

from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

import json

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "playlist-read-private"

def importCredentials():
    with open("credentials.json", 'r') as f:
            credentials = json.load(f)

    return credentials

def exportCredentials(credentials):
    with open("credentials.json", 'w') as f:
        json.dump(credentials, f, indent=4)
    
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

def getTokens(clientid, codeVerifier = None, code = None, refreshToken = None):
    url = "https://accounts.spotify.com/api/token"
    header = {"Content-Type": "application/x-www-form-urlencoded"}

    if refreshToken:
        body = {
            "grant_type" : "refresh_token",
            "refresh_token" : refreshToken,
            "client_id" : clientid
        }
    else:
        body = {
            "grant_type" : "authorization_code",
            "code" : code,
            "redirect_uri" : REDIRECT_URI,
            "client_id" : clientid,
            "code_verifier" : codeVerifier
        }

    response = requests.post(url, headers=header, data=body)
    response.raise_for_status()

    if "error" in response.json():
        if response.json()["error"] == "invalid_grant":
            return None
        else:
            sys.exit(f"Error - {response.json()["error"]} - exiting program.")

    pprint(response.json())

    if refreshToken:
        tokens = {
            "accessToken" : response.json()["access_token"],
            "refreshToken" : refreshToken,
            "expiry" : time.time() + response.json()["expires_in"]
        }
    else:
        tokens = {
            "accessToken" : response.json()["access_token"],
            "refreshToken" : response.json()["refresh_token"],
            "expiry" : time.time() + response.json()["expires_in"]
        }

    return tokens


def login(clientid):
    verifier = secrets.token_urlsafe(64);
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
    state = secrets.token_urlsafe(16)

    params = {
        "client_id" : clientid,
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

    if not server.result:
        sys.exit("Login failed - exiting program")

    if "error" in server.result:
        sys.exit(f"Login failed - {server.result["error"]} - exiting program.\n")

    if not secrets.compare_digest(server.result["state"], state):
        sys.exit("State mismatch - exiting program.\n")

    tokens = getTokens(clientid, codeVerifier=verifier, code=server.result["code"])

    return tokens

def getPlaylists(tokens):
    if tokens["expiry"] - time.time() > 60:
        getTokens(clientid=credentials["client-id"], refreshToken=tokens["refreshToken"])

    url = "https://api.spotify.com/v1/me/playlists"
    header = {"Authorization": f"Bearer {tokens["accessToken"]}"}

    response = requests.get(url, headers=header)
    response.raise_for_status()

    return response.json()

if __name__ == "__main__":
    credentials = importCredentials()
    clientid = credentials["client-id"]
    tokens = credentials["tokens"]

    if tokens["expiry"] == None or tokens["expiry"] - time.time() < 60:
        if tokens["expiry"] == None:
            tokens = login(clientid)
        else:
            tokens = getTokens(clientid=clientid, refreshToken=tokens["refreshToken"])
            if tokens == None:
                tokens = login(clientid)

    credentials["tokens"] = tokens
    pprint(tokens)

    exportCredentials(credentials)