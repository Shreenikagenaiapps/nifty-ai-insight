import pandas as pd

def get_mock_data():
    data = {
        'datetime': pd.date_range(start='2025-07-29 09:15', periods=6, freq='15min'),
        'open': [100, 102, 101, 103, 104, 106],
        'high': [102, 103, 104, 105, 107, 108],
        'low': [99, 101, 100, 102, 103, 105],
        'close': [101, 102, 103, 104, 106, 107],
        'volume': [1000, 1200, 1100, 1300, 1500, 1600]
    }
    return pd.DataFrame(data)