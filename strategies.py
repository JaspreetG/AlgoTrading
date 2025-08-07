import pandas as pd
import numpy as np


class Strategy:
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
            strategy_data['close'] / strategy_data['close'].shift(1))
        strategy_data.dropna(inplace=True)

        current_position = 0
        total_trades = 0
        total_log_returns = 0
        total_profit = 0
        total_loss = 0
        max_profit_booked = float('-inf')
        max_loss_booked = float('inf')
        winning_trades = 0
        losing_trades = 0
        risk_free_rate = 0.07  # Annual risk-free return

        for i in range(len(strategy_data)):
            row = strategy_data.iloc[i]
            prow = strategy_data.iloc[i - 1] if i > 0 else row

            if row['SMA_20'] > row['SMA_50'] and prow['SMA_20'] < prow['SMA_50']:
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

                    sell_price = (buy_price + target) if row['high'] >= (
                        buy_price + target) else (buy_price - stop_loss)
                    trade_return = sell_price - buy_price

                    if trade_return > 0:
                        total_profit += trade_return
                        winning_trades += 1
                        max_profit_booked = max(
                            max_profit_booked, trade_return)
                    else:
                        total_loss += abs(trade_return)
                        losing_trades += 1
                        max_loss_booked = min(max_loss_booked, trade_return)

                    print('Sell at', sell_price, 'Profit/Loss:', trade_return)

        hit_ratio = winning_trades / total_trades if total_trades > 0 else 0
        total_return = np.exp(total_log_returns) - 1
        average_daily_return = total_log_returns / \
            len(strategy_data) if len(strategy_data) > 0 else 0
        annualized_return = (1 + average_daily_return) ** 252 - 1
        annualized_volatility = strategy_data['increment'].std() * np.sqrt(252)
        sharpe_ratio = (annualized_return - risk_free_rate) / \
            annualized_volatility if annualized_volatility > 0 else 0

        max_profit_booked = max_profit_booked if max_profit_booked != float(
            '-inf') else 0
        max_loss_booked = max_loss_booked if max_loss_booked != float(
            'inf') else 0

        return {
            'Hit Ratio': hit_ratio,
            'Total Return': total_return,
            'Sharpe Ratio': sharpe_ratio,
            'Total Trades': total_trades,
            'Max Profit Booked': max_profit_booked,
            'Max Loss Booked': max_loss_booked,
        }

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

    def trends_momentum_strategy(self):
        strategy_data = self.data
        strategy_data['atr20'] = strategy_data['high'].rolling(
            20).mean()-strategy_data['low'].rolling(20).mean()
        strategy_data['20_day_sma'] = strategy_data['close'].rolling(
            window=20).mean()
        strategy_data.dropna(inplace=True)

        position = None
        total_trades = 0
        profitable_trades = 0
        target_price = 0
        entry_price = 0
        stop_loss = 0
        total_returns = 0

        for _, row in strategy_data.iterrows():
            if position is None:
                if row['close'] > row['20_day_sma']:
                    position = 'long'
                    entry_price = row['close']
                    stop_loss = row['close'] - 2 * row['atr20']
                    target_price = row['close'] + 4 * row['atr20']
                elif row['close'] < row['20_day_sma']:
                    position = 'short'
                    entry_price = row['close']
                    stop_loss = row['close'] + 2 * row['atr20']
                    target_price = row['close'] - 4 * row['atr20']
            elif position == 'long':
                if row['close'] >= target_price:
                    total_trades += 1
                    profitable_trades += 1
                    total_returns += np.log(target_price / entry_price)
                    position = None
                elif row['close'] <= stop_loss:
                    total_trades += 1
                    total_returns += np.log(stop_loss / entry_price)
                    position = None
            elif position == 'short':
                if row['close'] <= target_price:
                    total_trades += 1
                    profitable_trades += 1
                    total_returns += np.log(entry_price / target_price)
                    position = None
                elif row['close'] >= stop_loss:
                    total_trades += 1
                    total_returns += np.log(entry_price / stop_loss)
                    position = None

        accuracy = profitable_trades / total_trades if total_trades > 0 else 0
        total_returns = np.exp(total_returns)
        return accuracy, total_returns, total_trades

    def hammer_statergy(self):
        strategy_data = self.data
        strategy_data['sma20'] = strategy_data['close'].rolling(
            window=20).mean()
        strategy_data['mvol20'] = strategy_data['volume'].rolling(
            window=20).mean()
        strategy_data.dropna(inplace=True)
        current_position = 0
        total_trades = 0
        accuracy = 0
        total_log_returns = 0

        def is_hammer(open_price, high_price, low_price, close_price):
            body_size = abs(close_price - open_price)
            lower_shadow = min(open_price, close_price) - low_price
            return (body_size < 0.1 * (high_price - low_price)) and (lower_shadow >= 2 * body_size)

        for _, row in strategy_data.iterrows():
            if row['sma20'] > row['close'] and is_hammer(row['open'], row['high'], row['low'], row['close']) and row['volume'] > 1.5*row['mvol20']:
                if current_position == 0:
                    current_position = 1
                    buy_price = row['close']
                    stop_loss = row['low'] - 2*abs(row['open'] - row['close'])
                    target = row['close'] + 2*abs(buy_price - stop_loss)
                    print('Buy at', buy_price)
            elif current_position == 1:
                if row['low'] <= stop_loss or row['high'] >= target:
                    current_position = 0
                    total_trades += 1
                    sell_price = target if row['high'] >= target else stop_loss
                    accuracy += 1 if sell_price >= buy_price else 0
                    print('Sell at', sell_price)
                    total_log_returns += np.log(sell_price/buy_price)

        accuracy = accuracy / total_trades if total_trades > 0 else 0
        total_return = np.exp(total_log_returns) * 100 - 100
        return accuracy, total_return, total_trades

    def buysell(self):
        strategy_data = self.data
        df = pd.DataFrame(strategy_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        # Generate complete date range with original frequency and timezone
        all_dates = pd.date_range(start=df.index.min(
        ), end=df.index.max(), freq='D', tz='Asia/Kolkata')

        # Reindex DataFrame
        df = df.reindex(all_dates)

        # Fill missing rows with the previous day's data
        df.fillna(method='ffill', inplace=True)

        # Reset the index and rename the column
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'timestamp'}, inplace=True)

        print(df)
        strategy_data['increment'] = np.log(
            strategy_data['close']/strategy_data['close'].shift(1))
        strategy_data.dropna(inplace=True)

        current_position = 0
        total_trades = 0
        accuracy = 0
        total_log_returns = 0

        for _, row in strategy_data.iterrows():
            if row['increment'] > 0 and current_position == 0:
                current_position = 1
                buy_price = row['close']
                print('Buy at', buy_price)
            elif row['increment'] < 0 and current_position == 1:
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
