# OAUTH
#
#https://login.salesforce.com/services/oauth2/authorize?response_type=token&client_id=<your_client_id>&redirect_uri=<your_redirect_uri>
#
#
CLIENT_ID     = "<your_client_id>"
CLIENT_SECRET = "<your_client_secret>"
REDIRECT_URI  = "https://gae-salesforce.appspot.com/Callback"
LOGIN_URI     = "https://test.salesforce.com/"

# The reply is afer the '#' URL Encoded =>
# https://test.salesforce.com/services/oauth2/success#access_token=<client_access_token>&refresh_token=<client_access_token>&instance_url=<session_uri>&id=<id>&issued_at=<seconds_since_epoch>&signature=<hash>
#
ACCESS_TOKEN  = ''
INSTANCE_URL  = ''
REFRESH_TOKEN = ''
ISSUED_AT     = ''
