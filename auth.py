
from td.client import TDClient
from td.config import *


# Create a new session
TDSession = TDClient(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    credentials_path=CREDENTIALS_PATH,
    auth_flow='flask'
)

# Login to the session
TDSession.login()

accounts = TDSession.get_accounts(account=ACCOUNT_NUMBER)

print(accounts)
