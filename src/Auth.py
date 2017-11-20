import requests
import json

# Global IDs
LOGIN_CLIENT_ID = '71a7beb8-f21a-47d9-a604-2e71bee24fe0'
CLIENT_ID       = "b7cbf451-6bb6-4a5a-8913-71e61f462787"
DUID            = "0000000d000400808F4B3AA3301B4945B2E3636E38C0DDFC"
CLIENT_SECRET   = "zsISsjmCx85zgCJg"

class Auth:

    oauth = None
    last_error = None
    npsso = None
    grant_code = None
    refresh_token = None

    SSO_URL = 'https://auth.api.sonyentertainmentnetwork.com/2.0/ssocookie'
    CODE_URL = 'https://auth.api.sonyentertainmentnetwork.com/2.0/oauth/authorize'
    OAUTH_URL = 'https://auth.api.sonyentertainmentnetwork.com/2.0/oauth/token'


    login_request = {
                        "authentication_type": 'password',
                        "username": None,
                        'password': None,
                        'client_id': LOGIN_CLIENT_ID
                    }

    oauth_request = {
                        "app_context":      "inapp_ios",
                        "client_id":        CLIENT_ID,
                        "client_secret":    CLIENT_SECRET,
                        "code":             None,
                        "duid":             DUID,
                        "grant_type":       "authorization_code",
                        "scope": "capone:report_submission,psn:sceapp,user:account.get,user:account.settings.privacy.get,user:account.settings.privacy.update,user:account.realName.get,user:account.realName.update,kamaji:get_account_hash,kamaji:ugc:distributor,oauth:manage_device_usercodes"
                    }

    code_request = {
                        "state": "06d7AuZpOmJAwYYOWmVU63OMY",
                        "duid": DUID,
                        "app_context": "inapp_ios",
                        "client_id": CLIENT_ID,
                        "scope": "capone:report_submission,psn:sceapp,user:account.get,user:account.settings.privacy.get,user:account.settings.privacy.update,user:account.realName.get,user:account.realName.update,kamaji:get_account_hash,kamaji:ugc:distributor,oauth:manage_device_usercodes",
                        "response_type": "code"
                    }

    refresh_oauth_request = {
                                "app_context": "inapp_ios",
                                "client_id": CLIENT_ID,
                                "client_secret": CLIENT_SECRET,
                                "refresh_token": None,
                                "duid": DUID,
                                "grant_type": "refresh_token",
                                "scope": "capone:report_submission,psn:sceapp,user:account.get,user:account.settings.privacy.get,user:account.settings.privacy.update,user:account.realName.get,user:account.realName.update,kamaji:get_account_hash,kamaji:ugc:distributor,oauth:manage_device_usercodes"
                            }

    two_factor_auth_request = {
                                "authentication_type": "two_step",
                                "ticket_uuid": None,
                                "code": None,
                                "client_id": CLIENT_ID,
                              }

    def __init__(self, email, password, ticket='', code='', npsso=''):
        self.login_request['username'] = email
        self.login_request['password'] = password
        self.two_factor_auth_request['ticket_uuid'] = ticket
        self.two_factor_auth_request['code'] = code
        if npsso:
            self.npsso = npsso
            if (self.GrabCode() is False or self.GrabOAuth() is False):
                print("Error")
        else:
            if (self.GrabNPSSO() is False or self.GrabCode() is False or self.GrabOAuth() is False):
                print('Error')


    def GrabNPSSO(self):
        
        data = None
        
        if self.two_factor_auth_request['ticket_uuid'] and self.two_factor_auth_request['code']:
            
            # This code path currently doesn't do anything beyond load the JSON response.
            
            data = urllib.parse.urlencode(self.two_factor_auth_request).encode('utf-8')
            request = urllib.request.Request(self.SSO_URL, data = data)
            response = urllib.request.urlopen(request)
            data = json.loads(response.read().decode('utf-8'))
        else:
            response = requests.post(
                self.SSO_URL,
                data=self.login_request
            )
            data = response.json()
            
            print(json.dumps(data, indent=2))
            
            if hasattr(data, 'error'):
                return False
            if hasattr(data, 'ticket_uuid'):
                error = {
                            'error': '2fa_code_required',
                            'error_description': '2FA Code Required',
                            'ticket': data['ticket_uuid']
                }
                self.last_error = json.dumps(error)
                return False
            print(json.dumps(data, indent=2))
            print(response.status())
            self.npsso = data['npsso']
            return True

    def find_between(self, s, first, last ):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def GrabCode(self):
        response = requests.get(
            self.CODE_URL, 
            params=self.code_request,
            cookies=dict(npsso = self.npsso),
            allow_redirects=False,
        )
        grant_code = response.headers["X-NP-GRANT-CODE"]
        
        if not grant_code:
            error = {
                'error': 'invalid_np_grant',
                'error_description': 'Failed to obtain X-NP-GRANT-CODE',
                'error_code': 20
            }
            self.last_error = json.dumps(error)
            return False
        self.grant_code = grant_code
        return True
    
    def GrabNewTokens(refreshToken):
        refresh_oauth_request = {
            "app_context": "inapp_ios",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": None,
            "duid": DUID,
            "grant_type": "refresh_token",
            "scope": "capone:report_submission,psn:sceapp,user:account.get,user:account.settings.privacy.get,user:account.settings.privacy.update,user:account.realName.get,user:account.realName.update,kamaji:get_account_hash,kamaji:ugc:distributor,oauth:manage_device_usercodes"
        }

        refresh_oauth_request['refresh_token'] = refreshToken
        
        # Requests automatically form-encodes the data dictionary
        response = requests.post(self.OAUTH_URL, data = refresh_oauth_request)
        
        data = response.json()

        if hasattr(data, 'error'):
            return False

        return [data['access_token'], data['refresh_token']]

    def GrabOAuth(self):
        self.oauth_request['code'] = self.grant_code
        
        # Requests sets up the content-type encoding for us
        
        response = requests.post(self.OAUTH_URL, data = self.oauth_request)
        data = response.json()

        if hasattr(data, 'error'):
            self.last_error = data['body']
            return False

        self.oauth = data['access_token']
        self.refresh_token = data['refresh_token']

        return True

    def get_tokens(self):
        tokens = {
            "oauth": self.oauth,
            "refresh": self.refresh_token,
            "npsso": self.npsso
        }

        return tokens
