from fyers import FyersApp
from statergies import Statergy

if __name__ == "__main__":
    app = FyersApp()
    # authoring app, no need to run this code again
    # print(app.enable_app())

    from pprint import pprint
    profile = app.get_profile()
    print('===========================================')
    if profile['code'] != 200:
        print("\033[91mError in loading profile\033[0m")
        exit(1)
    # pprint(app.get_quote(['SBIN', 'RELIANCE']))
    # pprint(app.get_depth('SBIN'))
    # pprint(app.get_funds())
    # pprint(app.get_holdings())
    # pprint(app.get_order_book())
    # pprint(app.get_positions())
    # pprint(app.get_trade_book())

    data = app.fetch_historical_data(
        'HDFCBANK', resolution='D', data_from='2023-01-01', data_to='2024-03-27')
    print(data)
    statergy = Statergy(data)
    accuracy, returns, trades = statergy.macd_strategy()
    print("\033[1;32mAccuracy: {:.2f}% Returns: {:.2f}% Trades: {}\033[0m".format(
        accuracy * 100, returns, trades))
