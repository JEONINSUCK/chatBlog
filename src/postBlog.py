from datetime import datetime
from common import *

import requests
import json
import os

DEBUG_ENABLE = True

# load config.json data
with open("config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

# # set tistory config info
# tistory_code = config['AUTH']['TISTORY_CODE']
# tistory_app_id = config['AUTH']['TISTORY_APP_ID']
# tistory_secret_key = config['AUTH']['TISTORY_SECRET_KEY']
# tistory_url = config['AUTH']['TISTORY_URL']
# tistory_get_url = config['AUTH']['TISTORY_GET_URL']


class postBlog:
    def __init__(self) -> None:
        # set tistory config info
        self.tistory_code = config['AUTH']['TISTORY_CODE']
        self.tistory_app_id = config['AUTH']['TISTORY_APP_ID']
        self.tistory_secret_key = config['AUTH']['TISTORY_SECRET_KEY']
        self.tistory_url = config['AUTH']['TISTORY_URL']
        self.tistory_get_url = config['AUTH']['TISTORY_GET_URL']
        self.tistory_info_url = config['AUTH']['TISTORY_INFO_URL']
        self.tistory_category_url = config['AUTH']['TISTORY_CATEGORY_URL']
        self.tistory_post_url = config['AUTH']['TISTORY_POST_URL']
        self.tistory_access_token = config['AUTH']['TISTORY_ACCESS_TOKEN']
        
    def writeBlogPost(self, contents, title, category, visibility=1, acceptComment=1):
        debugPrint("[+] Write blog post run...")

        # set url parameter
        params = {
            'access_token' : self.tistory_access_token,
            'output' : 'json',
            'blogName' : self.getBlogName(),
            'title' : title,
            'content' : contents,
            'visibility' : visibility,
            'category' : category,
            'acceptComment' : acceptComment,
        }

        # request post url
        res = requests.post(self.tistory_post_url, data=params)
        if res.status_code == 200:
            debugPrint("[+] Write blog post OK...")
            return res.json()['tistory']['url']
        else:
            debugPrint("[-] Write blog post ERR...")
            print(res)
            return ERRORCODE._REQUEST_GET_ERR
    
    # need to update 'TISTORY_CODE' value everytime
    def getAccessToken(self):
        try:
            debugPrint("[+] Get access token run...")
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
                debugPrint("[+] Get access token OK...")
                return res.text.replace('access_token=','')
            else:
                debugPrint("[-] Get request ERR...")
                return ERRORCODE._REQUEST_GET_ERR
        except Exception as e:
            debugPrint("[-] Get access token FAIL...")
            # print("getAccessToken funcing exception: {0}".format(e))


    def getBlogInfo(self):
        try:
            debugPrint("[+] Get blog info run...")
            # set url parameter
            params = {
                'access_token' : self.tistory_access_token,
                'output' : 'json'
            }

            # request get url
            res = requests.get(self.tistory_info_url, params=params)
            if res.status_code == 200:
                debugPrint("[+] Get blog info OK...")
                return self.responsParse(res)
            else:
                debugPrint("[-] Get request ERR...")
                return ERRORCODE._REQUEST_GET_ERR
        except Exception as e:
            debugPrint("[-] Get blog info FAIL...")
            # print("getBlogInfo funcing exception: {0}".format(e))


    def getCategoryID(self):
        try:
            debugPrint("[+] Get category ID run...")
            
            categorys_dict = {}

            # set url parameter
            params = {
                'access_token' : self.tistory_access_token,
                'output' : 'json',
                'blogName' : self.getBlogName()
            }

            # request get url
            res = requests.get(self.tistory_category_url, params=params)
            if res.status_code == 200:
                res = self.responsParse(res)
                if "categories" in res:
                    for category_dict in res['categories']:
                        categorys_dict[category_dict['name']] = category_dict['id']

                    debugPrint("[+] Get category ID OK...")
                    return categorys_dict
                else:
                    debugPrint("[+] Category ID is not exist...")
                    return ERRORCODE._CATEGORY_ID_NOT_EXIST
            else:
                debugPrint("[-] Get request ERR...")
                return ERRORCODE._REQUEST_GET_ERR
        except Exception as e:
            debugPrint("[-] Get category ID FAIL...")
            # print("getCategoryID funcing exception: {0}".format(e))


    def getBlogName(self):
        return self.getBlogInfo()['blogs'][0]['name']

    def responsParse(self, src):
        return src.json()['tistory']['item']

if __name__ == '__main__':
    test_postBlog = postBlog()

    # print(test_postBlog.getAccessToken())

    # print(test_postBlog.getBlogInfo())
    # print(test_postBlog.getBlogName())
    print(test_postBlog.getCategoryID())
    file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH']])
    file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], os.listdir(file_path)[0]])
    test_contents = ""
    with open(file_path, 'r') as f:
        # test_contents = f.read()
        for line in f.readlines():
            test_contents += line
            test_contents += "\r\n"

        id = int(test_postBlog.getCategoryID()['헬스'])
        title = "체중 감량과 토닝을 위한 효과적인 운동"

        print(test_postBlog.writeBlogPost(test_contents, title, id))
    
    