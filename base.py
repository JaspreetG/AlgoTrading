import requests, time, hmac, base64, struct, os, json, traceback
from fyers_apiv3 import fyersModel
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class BaseFyersApp:
    def __init__(self):
        try:
            if not os.path.exists('config.json'):
                self.__create_config_file()
            config = json.load(open('config.json'))
            
            self._username = config['username']
            self.__totp_key = config['totp_key']
            self.pin = config['pin']
            self._client_id = config['client_id']
            self._secret_key = config['secret_key']
            self.__redirect_uri = config['redirect_uri']
            self.__access_token = config['access_token']
            self.__token_generated_on = config['token_generated_on']
            self.__config = config
            self.model = None
        except:
            traceback.print_exc()
            print("Error in reading config file")
            exit(1)

        if self._username == '' or self.__totp_key == '' or self.pin == '' or self._client_id == '' or self._secret_key == '' or self.__redirect_uri == '':
            print("Please fill the config file")
            exit(1)

    def __create_config_file(self):
        config = {
            'username': "",
            'totp_key': "",
            'pin': "",
            'client_id': "",
            'secret_key': "",
            'redirect_uri': "",
            'access_token': "",
            'token_generated_on': ""
            }
        with open('config.json', '+a') as f:
            json.dump(config,f)

    def enable_app(self):
        appSession = fyersModel.SessionModel(
            client_id=self._client_id,
            redirect_uri=self.__redirect_uri,
            response_type='code',
            state='state',
            secret_key=self._secret_key,
            grant_type='authorization_code')
        return appSession.generate_authcode()
    
    def __totp(self, key, time_step=30, digits=6, digest="sha1"):
        key = base64.b32decode(key.upper() + "=" * ((8 - len(key)) % 8))
        counter = struct.pack(">Q", int(time.time() / time_step))
        mac = hmac.new(key, counter, digest).digest()
        offset = mac[-1] & 0x0F
        binary = struct.unpack(">L", mac[offset : offset + 4])[0] & 0x7FFFFFFF
        return str(binary)[-digits:].zfill(digits)
    
    def __generate_token(self, refresh=False):
        if len(self.__access_token) > 10 and refresh == False:
            if datetime.fromtimestamp(self.__token_generated_on).date() == datetime.fromtimestamp(time.time()).date():
                return
        headers = {
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        }
        try:
            s = requests.Session()
            s.headers.update(headers)

            data1 = f'{{"fy_id":"{base64.b64encode(f"{self._username}".encode()).decode()}","app_id":"2"}}'
            r1 = s.post("https://api-t2.fyers.in/vagator/v2/send_login_otp_v2", data=data1)

            request_key = r1.json()["request_key"]
            data2 = f'{{"request_key":"{request_key}","otp":{self.__totp(self.__totp_key)}}}'
            r2 = s.post("https://api-t2.fyers.in/vagator/v2/verify_otp", data=data2)
            assert r2.status_code == 200, f"Error in r2:\n {r2.text}"

            request_key = r2.json()["request_key"]
            data3 = f'{{"request_key":"{request_key}","identity_type":"pin","identifier":"{base64.b64encode(f"{self.pin}".encode()).decode()}"}}'
            r3 = s.post("https://api-t2.fyers.in/vagator/v2/verify_pin_v2", data=data3)
            assert r3.status_code == 200, f"Error in r3:\n {r3.json()}"

            headers = {"authorization": f"Bearer {r3.json()['data']['access_token']}", "content-type": "application/json; charset=UTF-8"}
            data4 = f'{{"fyers_id":"{self._username}","app_id":"{self._client_id[:-4]}","redirect_uri":"{self.__redirect_uri}","appType":"100","code_challenge":"","state":"abcdefg","scope":"","nonce":"","response_type":"code","create_cookie":true}}'
            r4 = s.post("https://api.fyers.in/api/v2/token", headers=headers, data=data4)
            assert r4.status_code == 308, f"Error in r4:\n {r4.json()}"

            parsed = urlparse(r4.json()["Url"])
            auth_code = parse_qs(parsed.query)["auth_code"][0]

            session = fyersModel.SessionModel(client_id=self._client_id, 
                                            secret_key=self._secret_key, 
                                            redirect_uri=self.__redirect_uri, 
                                            response_type="code", 
                                            grant_type="authorization_code")
            session.set_token(auth_code)
            response = session.generate_token()
            self.__access_token = response["access_token"]
            self.__config['access_token'] = self.__access_token
            self.__config['token_generated_on'] = time.time()
            with open('config.json', 'w') as f:
                json.dump(self.__config,f)
            return self.__access_token
        except:
            traceback.print_exc()
            return None
        
    def _get_model(self):
        if self.model is None:
            self.__generate_token()
            self.model = fyersModel.FyersModel(client_id=self._client_id, token=self.__access_token, log_path=os.getcwd())
        return self.model
    


