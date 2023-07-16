from fastapi import FastAPI, Header, Request, Response
from pydantic import BaseModel
from urllib import parse
from datetime import datetime
from queue import Queue
try:
    from makeContent import makeContent
    from postBlog import postBlog
    from slackBot import Bot
    from common import *
except ModuleNotFoundError as e:
    from src.makeContent import makeContent
    from src.postBlog import postBlog
    from src.slackBot import Bot
    from src.common import *

import logging
import json
import os
import threading
import uvicorn

DEBUG_ENABLE = True

APP_NAME = "webhook-listener"
WEBHOOK_SECRET = "slackers"

evt = threading.Event()
input_que = Queue()
title_que = Queue()
app = FastAPI()

# load config.json data
with open("./config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

class webTool:
    def __init__(self) -> None:
        pass

    def bodyCheck(self, body_request):
        try:
            if body_request['actions'][0]['type'] == 'plain_text_input':
                # load the body data form
                with open("src/message_form/webhook_input_body_form.json", 'r', encoding="utf-8-sig") as bd_f:
                    form_data = json.load(bd_f)
                    # get key lists
                    form_keys = form_data.keys()
                    body_keys = body_request.keys()

                    if form_keys == body_keys:
                        return errorCode.BODY_ACT_INPUT.value
                    else:
                        return errorCode.BODY_CHK_FAIL.value
            elif body_request['actions'][0]['type'] == 'button':
                # load the body data form
                with open("src/message_form/webhook_button_body_form.json", 'r', encoding="utf-8-sig") as bd_f:
                    form_data = json.load(bd_f)
                    # get key lists
                    form_keys = form_data.keys()
                    body_keys = body_request.keys()

                    if form_keys == body_keys:
                        return errorCode.BODY_ACT_BUTTON.value
                    else:
                        return errorCode.BODY_CHK_FAIL.value
            else:
                return errorCode.BODY_CHK_FAIL.value
            
        except Exception as err:
            print(f"bodyCheck error: {err}")

    def getMsgTheme(self, body: dict):
        return body['message']['attachments'][0]['blocks'][1]['fields'][0]['text'].replace('*Theme:*',"")

    def getMsgTitle(self, body: dict):
        return body['message']['attachments'][0]['blocks'][1]['fields'][1]['text'].replace('*Title:*',"")

    def getMsgDate(self, body: dict):
        return body['message']['attachments'][0]['blocks'][1]['fields'][2]['text'].replace('*Date:*',"")

    def getMsgTime(self, body: dict):
        return body['message']['attachments'][0]['blocks'][1]['fields'][3]['text'].replace('*Time:*',"")

    def getActVal(self, body: dict):
        return body['actions'][0]['value']

    def getHeader(self, request: Request):
        return dict(request.headers.items())

    def getParm(self, request: Request):
        return dict(request.query_params.items())


class chatBlog:
    def __init__(self, webtool) -> None:
        web_tool = webtool

    # check the theme file and dir
    def theme_exist_chk(self):
        dir_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH']])
        # directory check
        if not os.path.exists(dir_path):
            return errorCode.THEME_DIR_NOT_EXIST.value
        # file check
        elif len(os.listdir(dir_path)) == 0:
            return errorCode.THEME_FILE_NOT_EXIST.value
        else:
            return errorCode.THEME_FILE_EXIST.value
    
    def run(self):
        gpt_bot = makeContent()
        blog_bot = postBlog()
        slack_bot = Bot()

        if self.theme_exist_chk() == errorCode.THEME_FILE_EXIST.value:       # exist the theme file before creating
            if gpt_bot.getCategoryTitle("운동") == None:          # do not have usable title
                pass
            else:
                pass
        
        else:
            slack_bot.sendInputMsg()

            evt.wait()
            if input_que.empty() == False:
                theme_name = input_que.get()
                print(theme_name)
            else:
                print("[-] Input Queue is empty...")
            
            gpt_bot.setTheme(theme_name)
            if gpt_bot.makeCategory() == errorCode.SUCCESS.value:
                print(f"[+] Make 5 titles about {theme_name} complete!!")



async def getBody(request: Request):
    # get body from webhook request
    parse_request_body = await request.body()
    # convert bytes data to string data and decode
    parse_request_body= parse.unquote(parse_request_body.decode('utf-8')).replace("payload=", "").replace("+", " ")
    # convert str to json type
    parse_request_body = json.loads(parse_request_body)

    return parse_request_body

async def print_request(request):
    print(f'request header       : {dict(request.headers.items())}' )
    print(f'request query params : {dict(request.query_params.items())}')  
    try : 
        print(f'request json         : {await request.json()}')
    except Exception as err:
        print(f'request body         : {await getBody(request)}')

        
@app.get("/")
async def get_test():
    return {"message" : "Hello world"}

# Request post operation
@app.post("/webhook", status_code=200)
async def webhook(request: Request):
    try:
        web_t = webTool()
        test_obj = chatBlog(web_t)
        header = web_t.getHeader(request)
        parm = web_t.getParm(request)
        body = await getBody(request)

        try:
            bchk = web_t.bodyCheck(body)
            if  bchk == errorCode.BODY_ACT_BUTTON.value:
                # await print_request(request)
                
                act_val = web_t.getActVal(body)
                if act_val == config['CONF']['APPROVE_ACT_VAL']:
                    print("[+] Approve button enter...")
                    print(web_t.getMsgTheme(body))
                    print(web_t.getMsgTitle(body))
                    print(web_t.getMsgDate(body))
                    print(web_t.getMsgTime(body))
                elif act_val == config['CONF']['DENY_ACT_VAL']:
                    print("[+] Deny button enter...")
                else:
                    print("action value not found")

                return {"status": "OK"}
            elif bchk == errorCode.BODY_ACT_INPUT.value:
                # TODO: 슬랙에서 온 응답 값 출력 및 시그널 신호 전송
                # TODO: uvicon 명령어로 이 함수를 실행시켜 놓고 python command로 main 함수를 실행시켜서 다른 프로세스라 서로 값을 못 주고 받나??
                # TODO: 이 함수도 python thread로 돌리고, main 함수도 thread로 돌리면 신호가 갈까???
                print("[+] Input data enter...")
                input_que.put(web_t.getActVal(body))
                evt.set()
                

        except Exception as e:
            return {"status": "body structure error"}
        

    except Exception as err:
        logging.error(f'could not print REQUEST: {err}')
        return {"status": "ERR"}

def web_th():
    uvicorn.run(app, port=8000)
    

if __name__ == '__main__':
    web_tool = webTool()
    chat_blog = chatBlog(web_tool)
    
    # log module init
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    file_logging = logging.FileHandler(f"{APP_NAME}.log")
    file_logging.setFormatter(formatter)
    logger.addHandler(file_logging)
    
    th_web = threading.Thread(target=web_th)
    th_chat_blog = threading.Thread(target=chat_blog.run)
    # th_chat_blog = threading.Thread(target=test_th1, args=(chat_blog,))
    # th_chablog = threading.Thread(target=chat_blog.run)
    th_chat_blog.start()
    th_web.start()
    

    
    
    
    # chat_blog.run()
    
    
    