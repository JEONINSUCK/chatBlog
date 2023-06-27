import requests
import json
import enum

# load config.json data
with open("config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

# # set tistory config info
# tistory_code = config['AUTH']['TISTORY_CODE']
# tistory_app_id = config['AUTH']['TISTORY_APP_ID']
# tistory_secret_key = config['AUTH']['TISTORY_SECRET_KEY']
# tistory_url = config['AUTH']['TISTORY_URL']
# tistory_get_url = config['AUTH']['TISTORY_GET_URL']
class errorCode(enum.Enum):
    SUCCESS = enum.auto()
    REQUEST_GET_ERR = enum.auto()


class postBlog:
    def __init__(self) -> None:
        # set tistory config info
        self.tistory_code = config['AUTH']['TISTORY_CODE']
        self.tistory_app_id = config['AUTH']['TISTORY_APP_ID']
        self.tistory_secret_key = config['AUTH']['TISTORY_SECRET_KEY']
        self.tistory_url = config['AUTH']['TISTORY_URL']
        self.tistory_get_url = config['AUTH']['TISTORY_GET_URL']
        self.tistory_info_url = config['AUTH']['TISTORY_INFO_URL']
        self.tistory_access_token = config['AUTH']['TISTORY_ACCESS_TOKEN']

    def getAccessToken(self):
        # set url parameter
        params = {
            'client_id' : self.tistory_app_id,
            'client_secret' : self.tistory_secret_key,
            'redirect_uri' : self.tistory_url,
            'code' : self.tistory_code,
            'grant_type' : 'authorization_code'
        }

        # request get url
        res = requests.get(self.tistory_get_url, params=params)
        if res.status_code == 200:
            return res.text.replace('access_token=','')
        else:
            return errorCode.REQUEST_GET_ERR.value

    def getBlogInfo(self):
        # set url parameter
        params = {
            'access_token' : self.tistory_access_token,
            'output' : 'json'
        }

        # request get url
        res = requests.get(self.tistory_info_url, params=params)
        if res.status_code == 200:
            return res.json()
        else:
            return errorCode.REQUEST_GET_ERR.value


if __name__ == '__main__':
    test_postBlog = postBlog()

    # print(test_postBlog.getAccessToken())
    print(test_postBlog.getBlogInfo())