from datetime import datetime
try:
    from common import *
except Exception as e:
    from src.common import *

import requests
import json
import os

logger = Mylogger()

# load config.json data
with open("config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)


class postBlog:
    def __init__(self) -> None:
        # set tistory config info
        self.tistory_code = config['AUTH']['TISTORY_CODE']
        self.tistory_app_id = config['AUTH']['TISTORY_APP_ID']
        self.tistory_secret_key = config['AUTH']['TISTORY_SECRET_KEY']
        self.tistory_url = config['AUTH']['TISTORY_URL']
        self.tistory_auth_url = config['AUTH']['TISTORY_AUTH_URL']
        self.tistory_info_url = config['AUTH']['TISTORY_INFO_URL']
        self.tistory_category_url = config['AUTH']['TISTORY_CATEGORY_URL']
        self.tistory_get_url = config['AUTH']['TISTORY_GET_URL']
        self.tistory_post_url = config['AUTH']['TISTORY_POST_URL']
        self.tistory_list_url = config['AUTH']['TISTORY_LIST_URL']
        self.tistory_access_token = config['AUTH']['TISTORY_ACCESS_TOKEN']
        
    def listBlogPost(self, page_num):
        logger.info("[+] List blog post run...")

        # set url parameter
        params = {
            'access_token' : self.tistory_access_token,
            'output' : "json",
            'blogName' : self.getBlogName(),
            'page' : page_num
        }

        res = requests.get(self.tistory_list_url, params=params)
        if res.status_code == 200:
            logger.info("[+] List blog post OK...")
            return res.json()['tistory']['item']['posts']
        else:
            logger.info("[-] List blog post ERR...")
            logger.info(res)
            return ERRORCODE._REQUEST_GET_ERR   

    def readBlogPost(self,post_id):
        logger.info("[+] Read blog post run...")

        # set url parameter
        params = {
            'access_token' : self.tistory_access_token,
            'output' : "json",
            'blogName' : self.getBlogName(),
            'postId' : post_id
        }

        res = requests.get(self.tistory_get_url, params=params)
        if res.status_code == 200:
            logger.info("[+] Read blog post OK...")
            return res.json()['tistory']['item']['content']
        else:
            logger.info("[-] Read blog post ERR...")
            logger.info(res)
            return ERRORCODE._REQUEST_GET_ERR   

    def writeBlogPost(self, contents, title, category, visibility=2, acceptComment=1):
        logger.info("[+] Write blog post run...")

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
            logger.info("[+] Write blog post OK...")
            return res.json()['tistory']['url']
        else:
            logger.info("[-] Write blog post ERR...")
            logger.info(res)
            return ERRORCODE._REQUEST_GET_ERR
    
    # need to update 'TISTORY_CODE' value everytime
    def getAccessToken(self):
        try:
            logger.info("[+] Get access token run...")
            # set url parameter
            params = {
                'client_id' : self.tistory_app_id,
                'client_secret' : self.tistory_secret_key,
                'redirect_uri' : self.tistory_url,
                'code' : self.tistory_code,
                'grant_type' : 'authorization_code'
            }

            # request get url
            res = requests.get(self.tistory_auth_url, params=params)
            if res.status_code == 200:
                logger.info("[+] Get access token OK...")
                return res.text.replace('access_token=','')
            else:
                logger.info("[-] Get request ERR...")
                return ERRORCODE._REQUEST_GET_ERR
        except Exception as e:
            logger.error("[-] Get access token FAIL...")
            logger.error("getAccessToken funcing exception: {0}".format(e))


    def getBlogInfo(self):
        try:
            logger.info("[+] Get blog info run...")
            # set url parameter
            params = {
                'access_token' : self.tistory_access_token,
                'output' : 'json'
            }

            # request get url
            res = requests.get(self.tistory_info_url, params=params)
            if res.status_code == 200:
                logger.info("[+] Get blog info OK...")
                return self.responsParse(res)
            else:
                logger.info("[-] Get request ERR...")
                return ERRORCODE._REQUEST_GET_ERR
        except Exception as e:
            logger.error("[-] Get blog info FAIL...")
            logger.error("getBlogInfo funcing exception: {0}".format(e))


    def getCategoryID(self):
        try:
            logger.info("[+] Get category ID run...")
            
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

                    logger.info("[+] Get category ID OK...")
                    return categorys_dict
                else:
                    logger.info("[+] Category ID is not exist...")
                    return ERRORCODE._CATEGORY_ID_NOT_EXIST
            else:
                logger.info("[-] Get request ERR...")
                return ERRORCODE._REQUEST_GET_ERR
        except Exception as e:
            logger.error("[-] Get category ID FAIL...")
            logger.error("getCategoryID funcing exception: {0}".format(e))


    def getBlogName(self):
        return self.getBlogInfo()['blogs'][0]['name']

    def responsParse(self, src):
        return src.json()['tistory']['item']

if __name__ == '__main__':
    test_postBlog = postBlog()

    # print(test_postBlog.getAccessToken())

    # print(test_postBlog.getBlogInfo())
    # print(test_postBlog.getBlogName())
    # print(test_postBlog.getCategoryID())
    file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH']])
    file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], os.listdir(file_path)[0]])
    test_contents = ""
    with open(file_path, 'r') as f:
       # test_contents = f.read()
       for line in f.readlines():
          test_contents += "<p>"
          test_contents += line
          test_contents += "</p>"

       id = int(test_postBlog.getCategoryID()['헬스'])
       title = "체중 감량과 토닝을 위한 효과적인 운동"

       print(test_postBlog.writeBlogPost(test_contents, title, id))

    # print(test_postBlog.listBlogPost(1))
    # print(test_postBlog.readBlogPost(36))
    
    