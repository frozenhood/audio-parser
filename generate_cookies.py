import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

refresh_token = sys.argv[1]
client_id = sys.argv[2]
client_secret = sys.argv[3]

creds = Credentials(
    None,
    refresh_token=refresh_token,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=client_id,
    client_secret=client_secret,
    scopes=["https://www.googleapis.com/auth/youtube.readonly"]
)

creds.refresh(Request())

with open("cookies.txt", "w") as f:
    f.write(f"# Netscape HTTP Cookie File\n")
    f.write(f".youtube.com\tTRUE\t/\tFALSE\t9999999999\tSID\t{creds.token}\n")