import pandas as pd
import numpy as np


class Statergy:
    def __init__(self, data):
        self.data = data

    def sma_strategy(self):
        strategy_data = self.data
        strategy_data['SMA_20'] = strategy_data['close'].rolling(
            window=20).mean()
        strategy_data['SMA_50'] = strategy_data['close'].rolling(
            window=50).mean()
        strategy_data['ATR_20'] = strategy_data['high'].rolling(
            window=20).mean() - strategy_data['low'].rolling(window=20).mean()
        strategy_data['increment'] = np.log(
            strategy_data['close']/strategy_data['close'].shift(1))
        strategy_data.dropna(inplace=True)

        current_position = 0
        total_trades = 0
        accuracy = 0
        total_log_returns = 0

        for i in range(len(strategy_data)):
            row = strategy_data.iloc[i]
            prow = strategy_data.iloc[i-1]
            prow = prow if i > 0 else row
            if row['SMA_20'] > row['SMA_50'] and prow['SMA_20'] < row['SMA_50']:
                if current_position == 0:
                    current_position = 1
                    buy_price = row['close']
                    stop_loss = row['ATR_20'] * 2
                    target = row['ATR_20'] * 6
                    print('Buy at', buy_price, 'Stop Loss:',
                          stop_loss, 'Target:', target)

            elif current_position == 1:
                total_log_returns += row['increment']
                if row['low'] <= (buy_price - stop_loss) or row['high'] >= (buy_price + target):
                    current_position = 0
                    total_trades += 1
                    sell_price = buy_price + \
                        target if row['high'] >= (
                            buy_price + target) else buy_price - stop_loss
                    accuracy += 1 if sell_price >= buy_price else 0

                    print('Sell at', sell_price)

        accuracy = accuracy / total_trades if total_trades > 0 else 0

        return accuracy, np.exp(total_log_returns), total_trades

    def macd_strategy(self):
        strategy_data = self.data

        # Calculate MACD line
        strategy_data['EMA_12'] = strategy_data['close'].ewm(
            span=12, min_periods=0, adjust=False).mean()
        strategy_data['EMA_26'] = strategy_data['close'].ewm(
            span=26, min_periods=0, adjust=False).mean()
        strategy_data['MACD'] = strategy_data['EMA_12'] - \
            strategy_data['EMA_26']

        # Calculate Signal line
        strategy_data['Signal'] = strategy_data['MACD'].ewm(
            span=9, min_periods=0, adjust=False).mean()

        # Define buy and sell conditions
        strategy_data['Buy'] = (strategy_data['MACD'] > strategy_data['Signal']) & (
            strategy_data['MACD'].shift(1) <= strategy_data['Signal'].shift(1))
        strategy_data['Sell'] = (strategy_data['MACD'] < strategy_data['Signal']) & (
            strategy_data['MACD'].shift(1) >= strategy_data['Signal'].shift(1))

        current_position = 0
        total_trades = 0
        accuracy = 0
        total_log_returns = 0

        for i, row in strategy_data.iterrows():
            if row['Buy'] and current_position == 0:
                current_position = 1
                buy_price = row['close']
                print('Buy at', buy_price)
            elif row['Sell'] and current_position == 1:
                current_position = 0
                total_trades += 1
                sell_price = row['close']
                accuracy += 1 if sell_price >= buy_price else 0
                log_return = np.log(sell_price / buy_price)
                total_log_returns += log_return
                print('Sell at', sell_price)

        accuracy = accuracy / total_trades if total_trades > 0 else 0
        total_return = np.exp(total_log_returns) * 100 - 100
        return accuracy, total_return, total_trades

    def big_bar_strategy(self):
        strategy_data = self.data
        strategy_data['big_bar'] = (
            strategy_data['high'] - strategy_data['low']) / strategy_data['close'].shift(1)
        strategy_data['increment'] = np.log(
            strategy_data['close']/strategy_data['close'].shift(1))
        strategy_data.dropna(inplace=True)

        current_position = 0
        total_trades = 0
        accuracy = 0
        total_log_returns = 0

        for _, row in strategy_data.iterrows():
            if row['big_bar'] > 0.005 and current_position == 0:
                current_position = 1
                buy_price = row['close']
                stop_loss = row['close'] - 2 * row['big_bar']*row['close']
                target = row['close'] + 4 * row['big_bar']*row['close']
                print('Buy at', buy_price, 'Stop Loss:',
                      stop_loss, 'Target:', target)
            elif current_position == 1:
                total_log_returns += row['increment']
                if row['low'] <= stop_loss or row['high'] >= target:
                    current_position = 0
                    total_trades += 1
                    sell_price = target if row['high'] >= target else stop_loss
                    accuracy += 1 if sell_price >= buy_price else 0
                    print('Sell at', sell_price)

        accuracy = accuracy / total_trades if total_trades > 0 else 0
        total_return = np.exp(total_log_returns) * 100 - 100
        return accuracy, total_return, total_trades
