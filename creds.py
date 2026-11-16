import json

def importCredentials():
    with open("credentials.json", 'r') as f:
            credentials = json.load(f)

    return credentials

def exportCredentials(credentials):
    with open("credentials.json", 'w') as f:
        json.dump(credentials, f, indent=4)