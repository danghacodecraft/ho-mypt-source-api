import requests
import json
from app.configs import app_settings

class MicrosoftAzureapis:
    token_url = ""
    client_id = ""
    client_secret = ""
    app_env = "production"

    def __init__(self):
        self.token_url = "https://login.microsoftonline.com/fptcloud.onmicrosoft.com/oauth2/v2.0/token"
        self.client_id = app_settings.AZURE_CLIENT_ID
        self.client_secret = app_settings.AZURE_CLIENT_SECRET

    def getAzureToken(self, authorizationCode, callbackUri):
        bodyData = {
            "grant_type": "authorization_code",
            "code": authorizationCode,
            "redirect_uri": callbackUri,
            "client_id": self.client_id,
            "scope": "openid profile",
            "client_secret": self.client_secret
        }
        print(bodyData)

        try:
            proxies = {
                "http": None,
                "https": "proxy.hcm.fpt.vn",
            }

            headersData = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            azureTokenResData = None
            if self.app_env == "staging" or self.app_env == "production":
                print("[MicrosoftAzureapis] Can set proxy khi goi API oauth2/v2.0/token boi vi app env la : " + self.app_env)
                azureTokenResData = requests.post(self.token_url, data=bodyData,
                                                      verify=True,
                                                      allow_redirects=False,
                                                      headers=headersData,
                                                      auth=(self.client_id, self.client_secret),
                                                      proxies=proxies,
                                                      timeout=5)
            else:
                print("[MicrosoftAzureapis] Khong can set proxy khi goi API oauth2/v2.0/token boi vi app env la : " + self.app_env)
                azureTokenResData = requests.post(self.token_url, data=bodyData,
                                                 verify=True,

                                                  allow_redirects=False,
                                                  headers=headersData,
                                                  auth=(self.client_id, self.client_secret),
                                                  timeout=5)
            print("[MicrosoftAzureapis] Ket qua API oauth2/v2.0/token : " + azureTokenResData.text)
            tokensData = json.loads(azureTokenResData.text)
            print(tokensData)
            if tokensData is None:
                return ""
            # chi lay ra id_token
            idToken = tokensData.get("id_token", "")
            idToken = str(idToken).strip()
            print("[MicrosoftAzureapis] Da lay duoc Azure Token tu API Azure: " + idToken)
            return idToken
        except Exception as ex:
            if isinstance(ex, requests.exceptions.ReadTimeout):
                print("[Azure] Error call API get Azure Token from Azure Code: Connection timeout")
            if isinstance(ex, requests.exceptions.ConnectionError):
                print("[Azure] Error call API get Azure Token from Azure Code: Connection Error")

        return ""