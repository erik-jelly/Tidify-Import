import oauth, creds

import time, requests
from pprint import pprint

import json

API_URL = None

if __name__ == "__main__":
    credentials = creds.importCredentials()
    clientid = credentials["tidal"]["client-id"]
    tokens = credentials["tidal"]["tokens"]

    print("Authenticating User...", end="", flush=True)

    if tokens["expiry"] == None or tokens["expiry"] - time.time() < 60:
        if tokens["expiry"] == None:
            tokens = oauth.login(clientid, 1)
        else:
            tokens = oauth.getTokens(clientid=clientid, refreshToken=tokens["refreshToken"])
            if tokens == None:
                tokens = oauth.login(clientid, 1)
    
    credentials["tidal"]["tokens"] = tokens

    pprint(tokens)

    print(f"\r\033[K{"Authentication Complete"}")

    creds.exportCredentials(credentials)