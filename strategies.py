import pandas as pd
import numpy as np

def atr(df, period):
    """Calculates the Average True Range"""
    try:
        high = df['High']
        low = df['Low']
        close = df['Close'].shift(1)
        
        tr1 = high - low
        tr2 = (high - close).abs()
        tr3 = (low - close).abs()
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
    except Exception as e:
        raise Exception(f"Error calculating ATR: {e}")

def heikin_ashi_candle(df):
    """Calculates Heikin Ashi candles"""
    try:
        ha_df = df.copy()
        ha_df['Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
        
        # Initialize Open with first row values
        ha_df['Open'] = (df['Open'] + df['Close']) / 2
        for i in range(1, len(df)):
            ha_df.iloc[i, ha_df.columns.get_loc('Open')] = (ha_df.iloc[i-1, ha_df.columns.get_loc('Open')] + ha_df.iloc[i-1, ha_df.columns.get_loc('Close')]) / 2
            
        ha_df['High'] = ha_df[['High', 'Open', 'Close']].max(axis=1)
        ha_df['Low'] = ha_df[['Low', 'Open', 'Close']].min(axis=1)
        return ha_df
    except Exception as e:
        raise Exception(f"Error calculating Heikin Ashi candles: {e}")

def ut_bot(df, sensitivity, atr_period, use_heikin_ashi):
    """
    Calculates UT Bot signals based on ATR trailing stops.
    Returns the DataFrame with 'Buy' and 'Sell' boolean columns.
    """
    try:
        if df.empty:
            return df

        if use_heikin_ashi:
            df = heikin_ashi_candle(df)
            
        df['ATR'] = atr(df, period=atr_period)
        
        # Vectorized / Iterative calculation for trailing stop
        ts = np.zeros(len(df))
        pos = np.zeros(len(df))
        
        close_prices = df['Close'].values
        atr_values = df['ATR'].values
        
        for i in range(1, len(df)):
            prev_ts = ts[i-1]
            prev_pos = pos[i-1]
            current_close = close_prices[i]
            prev_close = close_prices[i-1]
            current_atr = atr_values[i]
            
            # Calculate xATRTrailingStop
            if np.isnan(current_atr):
                ts[i] = 0
                pos[i] = 0
                continue

            if prev_close > prev_ts and current_close > prev_ts:
                ts[i] = max(prev_ts, current_close - current_atr * sensitivity)
            elif prev_close < prev_ts and current_close < prev_ts:
                ts[i] = min(prev_ts, current_close + current_atr * sensitivity)
            elif current_close > prev_ts:
                ts[i] = current_close - current_atr * sensitivity
            else:
                ts[i] = current_close + current_atr * sensitivity
                
            # Determine position
            if current_close > ts[i] and prev_close <= ts[i-1]:
                pos[i] = 1
            elif current_close < ts[i] and prev_close >= ts[i-1]:
                pos[i] = -1
            else:
                pos[i] = prev_pos
                
        df['Trailing_Stop'] = ts
        df['Position'] = pos
        
        # Generate Buy / Sell Signals (True when position changes)
        df['Buy'] = (df['Position'] == 1) & (df['Position'].shift(1) == -1)
        df['Sell'] = (df['Position'] == -1) & (df['Position'].shift(1) == 1)
        
        return df
    except Exception as e:
        raise Exception(f"Error calculating UT Bot signals: {e}")
