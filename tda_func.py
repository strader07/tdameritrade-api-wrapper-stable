from td.client import TDClient
from td.config import *

TDSession = TDClient(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    credentials_path=CREDENTIALS_PATH,
    auth_flow='flask'
)
TDSession.login()


def tdabuy(ticker="", amt=0.0):
    res_data = {
        "success": False,
        "message": ""
    }

    if not ticker:
        print("Ticker not defined.")
        res_data["message"] = "Ticker not defined."
        return res_data
    if amt <= 0:
        print("Amount should be greater than 0.")
        res_data["message"] = "Amount should be greater than 0."
        return res_data

    account_details = TDSession.get_accounts(
        account=ACCOUNT_NUMBER, fields=["positions", "orders"]
    )
    if account_details["securitiesAccount"]["type"] == "CASH":
        balance = account_details["securitiesAccount"]["currentBalances"]["cashAvailableForTrading"]
    else:
        balance = account_details["securitiesAccount"]["currentBalances"]["buyingPower"]
    quote = TDSession.get_quotes(instruments=[ticker])

    askPrice = quote[ticker]["askPrice"]
    if amt > balance:
        size = int(balance / askPrice)
        if size < 1:
            msg = f"Insufficient balance to buy a single share of {ticker}"
            print(msg)
            res_data["message"] = msg
            return res_data
    else:
        size = int(amt / askPrice)
        if size < 1:
            msg = f"Input amount is not big enough to buy a single share of {ticker}"
            print(msg)
            res_data["message"] = msg
            return res_data

    newOrder = {
        "complexOrderStrategyType": "NONE",
        "orderType": "LIMIT",
        "session": "NORMAL",
        "duration": "DAY",
        "price": askPrice,
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
            {
                "instruction": "BUY",
                "quantity": size,
                "instrument": {"symbol": ticker, "assetType": "EQUITY"},
            }
        ],
    }

    try:
        order_res = TDSession.place_order(account=ACCOUNT_NUMBER, order=newOrder)
        res_data["success"] = True
        res_data["message"] = f"Bought {size} shares of {ticker}!"
        return res_data
    except Exception as e:
        res_data["success"] = False
        res_data["message"] = e
        return res_data


def tdasell(ticker="", amt=0.0, sell_all=False):
    res_data = {
        "success": False,
        "message": ""
    }

    if not ticker:
        print("Ticker not defined.")
        res_data["message"] = "Ticker not defined."
        return res_data
    if amt <= 0 and not sell_all:
        print("Amount should be greater than 0.")
        res_data["message"] = "Amount should be greater than 0."
        return res_data

    account_details = TDSession.get_accounts(
        account=ACCOUNT_NUMBER, fields=["positions", "orders"]
    )

    positions = account_details["securitiesAccount"]["positions"]
    botsize = 0
    try:
        for position in positions:
            if position["instrument"]["symbol"] == ticker:
                botsize = botsize + position["longQuantity"]
    except Exception as e:
        print(e)
        res_data["message"] = e
        return res_data
    else:
        if botsize == 0:
            msg = f"{ticker} is not in trade."
            print(msg)
            res_data["message"] = msg
            return res_data

    quote = TDSession.get_quotes(instruments=[ticker])
    bidPrice = quote[ticker]["bidPrice"]

    if sell_all:
        size = botsize
    else:
        quote = TDSession.get_quotes(instruments=[ticker])

        bidPrice = quote[ticker]["bidPrice"]
        size = int(amt / bidPrice)
        if size > botsize:
            size = botsize

    newOrder = {
        "complexOrderStrategyType": "NONE",
        "orderType": "LIMIT",
        "session": "NORMAL",
        "duration": "DAY",
        "price": bidPrice,
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
            {
                "instruction": "SELL",
                "quantity": size,
                "instrument": {"symbol": ticker, "assetType": "EQUITY"},
            }
        ],
    }

    try:
        order_res = TDSession.place_order(account=ACCOUNT_NUMBER, order=newOrder)
        res_data["success"] = True
        res_data["message"] = f"Sold {size} shares of {ticker}!"
        return res_data
    except Exception as e:
        res_data["success"] = False
        res_data["message"] = e
        return res_data


def tdabal():
    account_details = TDSession.get_accounts(
        account=ACCOUNT_NUMBER, fields=["positions", "orders"]
    )

    if account_details["securitiesAccount"]["type"] == "CASH":
        available = account_details["securitiesAccount"]["currentBalances"]["cashAvailableForTrading"]
    else:
        available = account_details["securitiesAccount"]["currentBalances"]["buyingPower"]
    total = account_details["securitiesAccount"]["currentBalances"]["liquidationValue"]

    positions = account_details["securitiesAccount"]["positions"]
    assets = []
    if len(positions) < 1:
        return assets
    for position in positions:
        symbol = position["instrument"]["symbol"]
        bal = position["marketValue"]
        side = "LONG" if position["longQuantity"] > 0 else "SHORT"
        size = position["longQuantity"] if side == "LONG" else position["shortQuantity"]

        assets.append({
            symbol: {
                "shares": size,
                "usd": bal
            }})

    balance = {}
    balance["total"] = total
    balance["avail_usd"] = available
    balance["holds"] = assets

    return balance
