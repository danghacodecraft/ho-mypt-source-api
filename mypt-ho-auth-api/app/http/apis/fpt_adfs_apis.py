import requests
import json

class FptAdfsapis:
    token_url = ""
    client_id = "MyTin-PNC"
    client_secret = "dcVsRUZnzVTHez_ASDdZeTNzO5ZgtO7ZNoHyAzqV"

    def __init__(self):
        self.token_url = "https://adfs.fpt.com.vn/adfs/oauth2/token"
        self.client_id = "MyTin-PNC"
        self.client_secret = "dcVsRUZnzVTHez_ASDdZeTNzO5ZgtO7ZNoHyAzqV"

    def get_adfs_token(self, authorization_code, callback_uri):
        r = ""
        data = {'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': callback_uri}

        print(data)

        try:
            access_token_response = requests.post(self.token_url, data=data,
                                                  verify=True,
                                                  allow_redirects=False,
                                                  auth=(self.client_id, self.client_secret),
                                                  timeout=5)
            tokens = json.loads(access_token_response.text)
            print(tokens)
            access_token = tokens.get('access_token')
            print("Da lay duoc ADFS Token tu API ben ADFS: " + str(access_token))
            if access_token is not None:
                return access_token
        except Exception as ex:
            if isinstance(ex, requests.exceptions.ReadTimeout):
                # logger.info("api_auth :Connection Timeout")
                print("api_auth :Connection Timeout")
            if isinstance(ex, requests.exceptions.ConnectionError):
                # logger.info("api_auth :Connection Error")
                print("api_auth :Connection Timeout")
        return r