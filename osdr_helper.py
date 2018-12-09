# Helper to request token from server. Also stores credentials and urls in one place.

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import platform

host = "https://api.dev.dataledger.io/osdr/v1/api"
blob_host = "https://api.dev.dataledger.io/blob/v1/api/blobs"
scope = ['api', 'osdr-api']

client_id = 'resource_owner_client'
client_secret = 'my_top_secret_key'
username = 'Jason'
password = 'qqq123'
bucketId = '8332cb0a-e8ba-4585-b9e4-e64399e8b4bd'

def getToken():
    token_url = "https://identity.your-company.com/core/connect/token"
    oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id), scope=scope)
    if platform.system() == 'Windows':
        token = oauth.fetch_token(token_url=token_url,
                username=username, password=password, client_id=client_id,
                client_secret=client_secret)
    else:
        token = oauth.fetch_token(token_url=token_url,
                username=username, password=password, client_id=client_id,
                client_secret=client_secret, scope=scope)
    return token, oauth
