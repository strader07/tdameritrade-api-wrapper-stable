
from tda_func import tdabuy, tdasell, tdabal
import json


# tdabuy(ticker="AAPL", amt=100.00)
# tdasell(ticker="TSLA", amt=100.00, sell_all=False)
print(json.dumps(tdabal(), indent=4))