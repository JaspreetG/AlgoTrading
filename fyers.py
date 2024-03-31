from base import BaseFyersApp
import pandas as pd
import time
import traceback


class FyersApp(BaseFyersApp):
    def get_profile(self):
        try:
            fyers = self._get_model()
            return fyers.get_profile()
        except:
            traceback.print_exc()
            return None

    def get_depth(self, symbol, segment='EQ', exchange='NSE'):
        data = {
            "symbol": "{}:{}-{}".format(exchange, symbol, segment),
            "ohlcv_flag": "1"
        }
        return self.__get_model().depth(data=data)

    def get_quote(self, symbols=[], segment='EQ', exchange='NSE'):
        if len(symbols) == 0:
            return 'No symbols provided'

        symbols = '{}:'.format(exchange) + '-{},{}:'.format(segment,
                                                            exchange).join(symbols) + '-{}'.format(segment)
        data = {"symbols": symbols}
        return self.__get_model().quotes(data=data)

    def get_funds(self):
        try:
            return self.__get_model().funds()
        except:
            traceback.print_exc()
            return None

    def get_holdings(self):
        try:
            return self.__get_model().holdings()
        except:
            traceback.print_exc()
            return None

    def get_order_book(self, order_id=""):
        try:
            if order_id != "":
                return self.__get_model().orderbook(data={"id": order_id})
            else:
                return self.__get_model().orderbook()
        except:
            traceback.print_exc()
            return None

    def get_positions(self):
        try:
            return self.__get_model().positions()
        except:
            traceback.print_exc()
            return None

    def get_trade_book(self):
        try:
            return self.__get_model().tradebook()
        except:
            traceback.print_exc()
            return None

    def get_historical_data(self, symbol, resolution='D', data_from='2024-01-01', data_to='2024-03-27', segment='EQ', exchange='NSE'):
        try:
            data = {
                "symbol": "{}:{}-{}".format(exchange, symbol, segment),
                "resolution": resolution,
                "date_format": "1",
                "range_from": data_from,
                "range_to": data_to,
                "cont_flag": "1",
            }
            fyers = self._get_model()
            candles_data = fyers.history(data=data)
            return candles_data
        except:
            traceback.print_exc()
            return None

    def fetch_historical_data(self, symbol, resolution, data_from, data_to):
        MAX_DAYS_PER_REQUEST = {
            'D': 366, '5S': 30, '10S': 30, '15S': 30, '30S': 30, '45S': 30,
            '1': 100, '2': 100, '3': 100, '5': 100, '10': 100, '15': 100,
            '20': 100, '30': 100, '60': 100, '120': 100, '240': 100
        }
        MAX_REQUESTS_PER_SECOND = 6

        data_from_dt, data_to_dt = pd.to_datetime(
            data_from), pd.to_datetime(data_to)
        candles_data = []

        num_days = (data_to_dt - data_from_dt).days
        num_requests = (num_days // MAX_DAYS_PER_REQUEST[resolution]) + (
            1 if num_days % MAX_DAYS_PER_REQUEST[resolution] != 0 else 0)

        for i in range(num_requests):
            start_date = data_from_dt + \
                pd.Timedelta(days=i * MAX_DAYS_PER_REQUEST[resolution])
            end_date = min(data_from_dt + pd.Timedelta(days=(i + 1)
                           * MAX_DAYS_PER_REQUEST[resolution] - 1), data_to_dt)
            request_data_from, request_data_to = start_date.strftime(
                '%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

            data = self.get_historical_data(
                symbol, resolution=resolution, data_from=request_data_from, data_to=request_data_to)

            while data['code'] == 429:
                time.sleep(2)
                data = self.get_historical_data(
                    symbol, resolution=resolution, data_from=request_data_from, data_to=request_data_to)

            if data['code'] != 200:
                print('\033[1;31;40mERROR IN FETCHING DATA\033[0;0m')
                return exit(1)
            candles_data.extend(data['candles'])

            if (i + 1) % MAX_REQUESTS_PER_SECOND == 0:
                time.sleep(2)

        historical_df = pd.DataFrame(candles_data, columns=[
                                     'timestamp', 'open', 'high', 'low', 'close', 'volume'])
        historical_df['timestamp'] = pd.to_datetime(
            historical_df['timestamp'], unit='s', origin='unix').dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
        historical_df[['open', 'high', 'low', 'close']] = historical_df[[
            'open', 'high', 'low', 'close']].astype(float)
        historical_df['volume'] = historical_df['volume'].astype(int)
        historical_df.set_index('timestamp', inplace=True)

        return historical_df
