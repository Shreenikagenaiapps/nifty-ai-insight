from kite_login import kite
import pandas as pd
from datetime import datetime, timedelta, time
from kiteconnect import KiteConnect
import os


def get_reliance_data():
    instrument_token = 738561  # Reliance's instrument token for NSE
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)  # last 1 month

    try:
        data = kite.historical_data(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval="day",  # Daily candles
            continuous=False
        )
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print("Error fetching Reliance data:", e)
        return pd.DataFrame()  # return empty dataframe on failure

###bank nifty code below###

def get_nifty_data():
    kite = KiteConnect(api_key=os.getenv("KITE_API_KEY"))
    kite.set_access_token(os.getenv("KITE_ACCESS_TOKEN"))

    instrument_token = 256265  # NIFTY index

    # Get today's date and form the time range
    today = datetime.today().date()
    from_datetime = datetime.combine(today, time(9, 15))   # Market open
    to_datetime = datetime.combine(today, time(15, 30))    # Market close

    candles = kite.historical_data(
        instrument_token,
        from_datetime,
        to_datetime,
        "15minute"
    )

    return pd.DataFrame(candles)
