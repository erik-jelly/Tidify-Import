import creds

import time, sys, secrets, hashlib, base64, webbrowser, requests

from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

REDIRECT_URL = "http://127.0.0.1:8888/callback"
SCOPES = {"spotify" : "playlist-read-private", "tidal" : "playlists.write"}

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


# service = 0 (spotify), service = 1 (tidal)
def getTokens(clientid, service, codeVerifier = None, code = None, refreshToken = None):
    if service == 1:
        url = "https://auth.tidal.com/v1/oauth2/token"
    else:
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
            "redirect_uri" : REDIRECT_URL,
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

    #pprint(response.json())

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

# service = 0 (spotify), service = 1 (tidal)
def login(clientid, service):
    verifier = secrets.token_urlsafe(64);
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
    state = secrets.token_urlsafe(16)

    params = {
        "client_id" : clientid,
        "response_type" : 'code',
        "redirect_uri" : REDIRECT_URL,
        "state" : state,
        "scope" : SCOPES["tidal"] if service else SCOPES["spotify"],
        "code_challenge_method" : "S256",
        "code_challenge" : challenge
    }

    if service:
        url = "https://login.tidal.com/authorize?" + urlencode(params)
    else:
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

    tokens = getTokens(clientid, service, codeVerifier=verifier, code=server.result["code"])

    return tokens
