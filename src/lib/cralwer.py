try:
    from logger import *
except Exception as e:
    from lib.logger import *

import requests, re, os
from dotenv import load_dotenv
load_dotenv()


class BlogManager:    
    '''
        init configuration vai environment variables
    '''
    def __init__(self) -> None:
        self.logger = Mylogger()
        
        print("plz, refrer https://tistory.github.io/document-tistory-apis/apis")
        print("plz, refrer https://notice.tistory.com/2664")
        # load env
        
        # tistory
        self.tistory_app_id = os.environ.get("TISTORY_APP_ID", "")
        self.tistory_secret_key = os.environ.get("TISTORY_SECRET_KEY", "")
        
        # prefix
        self.blog_url = os.environ.get("TISTORY_BLOG_URL", "")
        self.tistory_url = os.environ.get("TISTORY_URL", "")
        
        # var
        self.tistory_access_code = ''
        self.tistory_access_token = ''
        self.blog_info = {}
        self.categorys_dict = {}
    
    
    '''
        get all post 
    '''
    def listPost(self, page_num=1):
        self.logger.info("[+] List blog post run...")

        # set url parameter
        params = {
            'access_token' : self.tistory_access_token,
            'output' : "json",
            'blogName' : self.blog_info["name"],
            'page' : page_num
        }

        res = requests.get(f"{self.tistory_url}/apis/post/list", params=params)
        if res.status_code == 200:
            self.logger.info("[+] List blog post OK...")
            return res.json()['tistory']['item']['posts']
        else:
            self.logger.info("[-] List blog post ERR...")
            self.logger.info(res)
            return ERRORCODE._REQUEST_GET_ERR   

    '''
        read post via post_id
    '''
    def readPost(self, post_id = 0):
        
        if int(post_id) < 1 or post_id == '':
            raise ValueError("require post id ")
        
        self.logger.info("[+] Read blog post run...")

        # set url parameter
        params = {
            'access_token' : self.tistory_access_token,
            'output' : "json",
            'blogName' : self.blog_info["name"],
            'postId' : post_id
        }

        res = requests.get(f"{self.tistory_url}/apis/post/read", params=params)
        if res.status_code == 200:
            self.logger.info("[+] Read blog post OK...")
            return res.json()['tistory']['item']['content']
        else:
            self.logger.info("[-] Read blog post ERR...")
            self.logger.info(res.text)
            return ERRORCODE._REQUEST_GET_ERR   

    def writePost(self, title, contents, category, visibility=2, acceptComment=1):
        self.logger.info("[+] Write blog post run...")

        # set url parameter
        params = {
            'access_token' : self.tistory_access_token,
            'output' : 'json',
            'blogName' : self.blog_info["name"],
            'title' : title,
            'content' : contents,
            # visibility: 발행상태 (0: 비공개 - 기본값, 1: 보호, 3: 발행)
            'visibility' : 0,
            'category' : category,
            'acceptComment' : acceptComment,
            "tag" : "test,rpa",
            "slogan"  : "address??",
            # if set the furture time, reserve post
            "published" : "",
        }

        # request post url
        res = requests.post(f"{self.tistory_url}/apis/post/write", data=params)
        if res.status_code == 200:
            self.logger.debug(res.json())
            self.logger.info("[+] Write blog post OK...")
            return res.json()['tistory']
        else:
            self.logger.info("[-] Write blog post ERR...")
            self.logger.info(res)
            return ERRORCODE._REQUEST_GET_ERR
    
    '''
        get access token for write post, get post, etc,,,,
    '''
    def getAccessToken(self):
        try:
            self.logger.info("[+] Get access token run...")
            
            if not self.tistory_access_code:
                self.getAccessCode()
                
            # set url parameter
            params = {
                'client_id' : self.tistory_app_id,
                'client_secret' : self.tistory_secret_key,
                'redirect_uri' : self.blog_url,
                'code' : self.tistory_access_code,
                'grant_type' : 'authorization_code'
            }

            # request get url
            res = requests.get(f"{self.tistory_url}/oauth/access_token", params=params)
            if res.status_code == 200:
                self.logger.info("[+] Get access token OK...")
                self.tistory_access_token = res.text.replace('access_token=','')
            else:
                self.logger.info("[-] Get request ERR...")
                self.logger.info(f"{ERRORCODE._REQUEST_GET_ERR}, {res.text}")
        except Exception as e:
            self.logger.error("[-] Get access token FAIL...")
            self.logger.error("getAccessToken funcing exception: {0}".format(e))
    
    '''
        excute before get access token
    '''
    def getAccessCode(self):
        
        try:
            self.logger.info("[+] Get authorize code run...")
            
            params = {
                'client_id' : self.tistory_app_id,
                'redirect_uri' : self.blog_url,
                'response_type' : "code",
            }
            
            # 보안상 없으면 크롤링으로 처리됨
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
                'Cache-Control': 'max-age=0',
                'Cookie': '_clck=6p71b0|2|fd5|0|1285; TOP-XSRF-TOKEN=235c969f-cba2-43a5-8afe-85159f9516b8; __T_=1; FCNEC=%5B%5B%22AKsRol_lO-fm-vQqwwn0WH66vKdOLkkmX9nWpc4Ec_tTIzAV1vCgclAduufY0zTlBUvJNY3cH7aW81NQiK9EFkEPEmnyvTT3jjgkLSYncLagS6cbxyTV_lBya-USfvPgEbXi7Bp_exsNywkXYcXL2A6Tc-LLaTMxVg%3D%3D%22%5D%2Cnull%2C%5B%5D%5D; TSAL=1; TSSESSION=82d1b88a32526fb240c5eda1610e20c06b5094ff; _T_ANO=nwtekqCGnG+NyW5lKg+31Pnygno2cmXk7yCPEhu3sS20x5C203+RB7qsAFB7STJXmQ3DfLAWhUBA4PQWhzif2w3Hl/w2k9PVFI95+X1pKtFrC0UGvQQ8DsZg6jO7hEHrMShbuGeqdXcJVBDv/LOfpKPi+bEIjEJ0qdDSRVbfwR35sIpYw/rxmnuA3Q3rbEkcA7GAkmlzjx4CzwVMYpstWGEkhAuAQiNDJCDKJH8pCmOEwRypG84HGN0wbxeb8XrbcGG7n6ox4AWI/4pil2XczH3FlgY6tS70q85ZytdDJBJgCNwZUyMK9X1IGYEyPF3Z/Iqwb84eIVj0RXO3bO7mYw==;',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }


            # request get url
            res = requests.get(f"{self.tistory_url}/oauth/authorize", params=params, headers=headers)
            
            if res.status_code == 200:
                
                self.tistory_access_code = ''

                matches = re.finditer(r"code=(.*)&", res.text, re.MULTILINE)

                for matchNum, match in enumerate(matches, start=1):
                    self.logger.debug("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
                    self.tistory_access_code = match.groups()[len(match.groups()) - 1]
                        
                if self.tistory_access_code == '':
                    raise ValueError("Invalid access code")

                self.logger.info("[+] Get access code OK...")
                
            else:
                link = f"{self.tistory_url}/oauth/authorize?client_id={self.tistory_app_id}&redirect_uri={self.blog_url}&response_type=code"
                self.logger.info(f"try visit this link : {link}")
                self.logger.info("[-] Get request ERR...")
                self.logger.info(res.text)
                return ERRORCODE._REQUEST_GET_ERR
            
        except Exception as e:
            self.logger.error("[-] Get access code FAIL...")
            self.logger.error("getAccessCode funcing exception: {0}".format(e))

    '''
        get tistory blog info via matched blog's url
    '''
    def getInfo(self):
        try:
            # cache
            if self.blog_info != {}:
                return self.blog_info
            
            self.logger.info("[+] Get blog info run...")
            # set url parameter
            params = {
                'access_token' : self.tistory_access_token,
                'output' : 'json'
            }

            # request get url
            res = requests.get(f"{self.tistory_url}/apis/blog/info", params=params)
            if res.status_code == 200:
                self.logger.info("[+] Get blog info OK...")
                
                rv = res.json()
                for x in rv['tistory']["item"]["blogs"]:
                    if x["url"] != self.blog_url:
                        continue
                    
                    self.blog_info = x
                
                return self.blog_info
            else:
                self.logger.info("[-] Get request ERR...")
                self.logger.info(res.text)
                return ERRORCODE._REQUEST_GET_ERR
        except Exception as e:
            self.logger.error("[-] Get blog info FAIL...")
            self.logger.error("getBlogInfo funcing exception: {0}".format(e))

    '''
        get tistory blog category via matched blog's url
    '''
    def getCategoryID(self):
        try:
            # cache
            if self.categorys_dict != {}:
                return self.categorys_dict
            self.logger.info("[+] Get category ID run...")
            
            self.categorys_dict = {}

            # set url parameter
            params = {
                'access_token' : self.tistory_access_token,
                'output' : 'json',
                'blogName' : self.blog_info["name"]
            }

            # request get url
            res = requests.get(f"{self.tistory_url}/apis/category/list", params=params)
            if res.status_code == 200:
                rv = res.json()
                res = rv["tistory"]["item"]
                if "categories" in res:
                    for category_dict in res['categories']:
                        self.categorys_dict[category_dict['name']] = category_dict['id']
                        self.logger.info(f"update : {category_dict['name']}, {category_dict['id']}")

                    self.logger.info("[+] Get category ID OK...")
                    return self.categorys_dict
                else:
                    self.logger.info("[+] Category ID is not exist...")
                    return ERRORCODE._CATEGORY_ID_NOT_EXIST
            else:
                self.logger.info("[-] Get request ERR...")
                return ERRORCODE._REQUEST_GET_ERR
        except Exception as e:
            self.logger.error("[-] Get category ID FAIL...")
            self.logger.error("getCategoryID funcing exception: {0}".format(e))

if __name__ == '__main__':
    
    blog = BlogManager()
    blog.getAccessToken()
    blog.getInfo()
    blog.getCategoryID()

    print(blog.blog_info)
    
    rv = blog.listPost()
    
    print(f"blog.listPost() : {rv}")
    
    post = blog.writePost("test title", "test content", "일상")
    
    rv = blog.readPost(post["postId"])
    
    print(f"blog.readPost() : {rv}")
    
    print(rv)
