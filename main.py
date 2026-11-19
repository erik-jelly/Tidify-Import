import oauth, creds, spotify, tidal
import time

SPOTIFY, TIDAL = range(2)

def authentication(tokens, service):
    if tokens["expiry"] == None or tokens["expiry"] - time.time() < 60:
        if tokens["expiry"] == None:
            tokens = oauth.login(clientid, service)
        else:
            tokens = oauth.getTokens(clientid=clientid, service=service, refreshToken=tokens["refreshToken"])
            if tokens == None:
                tokens = oauth.login(clientid, service)

    return tokens

if __name__ == "__main__":
    credentials = creds.importCredentials()

    clientid = credentials["spotify"]["client-id"]
    tokens = credentials["spotify"]["tokens"]

    print("Spotify Authenticating User...", end="", flush=True)

    tokens = authentication(tokens, SPOTIFY)
    
    credentials["spotify"]["tokens"] = tokens
    creds.exportCredentials(credentials)

    print(f"\r\033[K{"Spotify Authentication Complete"}")

    print("Exporting Playlists from Spotify...")

    playlists = spotify.getPlaylists(tokens["accessToken"])
    
    print("Export Complete!")

    clientid = credentials["tidal"]["client-id"]
    tokens = credentials["tidal"]["tokens"]

    print("Tidal Authenticating User...", end="", flush=True)

    tokens = authentication(tokens, TIDAL)
    
    credentials["tidal"]["tokens"] = tokens
    creds.exportCredentials(credentials)

    print(f"\r\033[K{"Tidal Authentication Complete"}")

    print("Importing Playlists to Tidal...")

    for playlist in playlists:
        playlistid = tidal.createPlaylist(tokens["accessToken"], playlist)
        for song in playlist["songs"]:
            tidal.addSong(tokens["accessToken"], playlistid, song)

    print("Import Complete!")