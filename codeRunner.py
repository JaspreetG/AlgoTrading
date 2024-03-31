 statergy = Statergy(data);
    accuracy, returns, trades = statergy.macd_strategy()
    print("\033[1;32mAccuracy: {:.2f}% Returns: {:.2f}% Trades: {}\033[0m".format(accuracy * 100, returns, trades))