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
import schedule
import time


APP_NAME = "webhook-listener"
WEBHOOK_SECRET = "slackers"

chatblog_timeout = False

logger = Mylogger()

evt = threading.Event()
input_que = Queue()
button_que = Queue()
slash_que = Queue()
app = FastAPI()

# load config.json data
with open("./config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

class webTool:
    def __init__(self) -> None:
        pass

    def bodyCheck(self, body_request):
        try:
            if 'actions' in body_request:               # if block message
                if body_request['actions'][0]['type'] == 'plain_text_input':
                    # load the body data form
                    with open("src/message_form/webhook_input_body_form.json", 'r', encoding="utf-8-sig") as bd_f:
                        form_data = json.load(bd_f)
                        # get key lists
                        form_keys = form_data.keys()
                        body_keys = body_request.keys()

                        if form_keys == body_keys:
                            return ERRORCODE._BODY_ACT_INPUT
                        else:
                            return ERRORCODE._BODY_CHK_FAIL
                elif body_request['actions'][0]['type'] == 'button':
                    # load the body data form
                    with open("src/message_form/webhook_button_body_form.json", 'r', encoding="utf-8-sig") as bd_f:
                        form_data = json.load(bd_f)
                        # get key lists
                        form_keys = form_data.keys()
                        body_keys = body_request.keys()

                        if form_keys == body_keys:
                            return ERRORCODE._BODY_ACT_BUTTON
                        else:
                            return ERRORCODE._BODY_CHK_FAIL
                elif body_request['actions'][0]['type'] == 'multi_static_select':
                    # load the body data form
                    with open("src/message_form/webhook_select_body_form.json", 'r', encoding="utf-8-sig") as bd_f:
                        form_data = json.load(bd_f)
                        # get key lists
                        form_keys = form_data.keys()
                        body_keys = body_request.keys()
                        if form_keys == body_keys:
                            return ERRORCODE._BODY_ACT_SELECT
                        else:
                            return ERRORCODE._BODY_CHK_FAIL
                else:
                    return ERRORCODE._BODY_CHK_FAIL
            else:              # if slash command
                if body_request['command'] == '/chatblog':
                    return ERRORCODE._BODY_CHK_CMD
                else:
                    return ERRORCODE._BODY_CHK_FAIL
            
        except Exception as err:
            logger.error(f"bodyCheck error: {err}")

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
    
    def getSelVal(self, body: dict):
        return body['actions'][0]['selected_options'][0]['text']['text']

    def getHeader(self, request: Request):
        return dict(request.headers.items())

    def getParm(self, request: Request):
        return dict(request.query_params.items())


class chatBlog:
    def __init__(self) -> None:
        self.theme = ""
        self.title = ""
        self.gpt_bot = makeContent()
        self.blog_bot = postBlog()
        self.slack_bot = Bot()

    # check the theme file and dir
    def theme_exist_chk(self):
        dir_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH']])
        # directory check
        if not os.path.exists(dir_path):
            return ERRORCODE._THEME_DIR_NOT_EXIST
        # file check
        elif len(os.listdir(dir_path)) == 0:
            return ERRORCODE._THEME_FILE_NOT_EXIST
        else:
            return ERRORCODE._THEME_FILE_EXIST
    def get_usable_title(self):
        for theme in self.gpt_bot.getThemeSrc():
            get_title_src = self.gpt_bot.getTitleSrc(theme)
            if get_title_src == ERRORCODE._TITLE_USED:          # do not have usable title
                    continue
            elif get_title_src == ERRORCODE._THEME_NOT_EXIST:
                logger.info("[-] Theme file not exist...")
            else:
                self.set_theme(theme)
                return get_title_src
            
        return ERRORCODE._TITLE_ALL_USED

    def input_request_proc(self):
        theme_list = self.blog_bot.getCategoryID().keys()
        self.slack_bot.sendInputMsg(theme_list)

        evt.wait()
        evt.clear()
        if input_que.empty() == False:
            theme_name = input_que.get()
            logger.info(theme_name)
        else:
            logger.info("[-] Input Queue is empty...")
        
        self.gpt_bot.setTheme(theme_name)
        if self.gpt_bot.makeCategory() == ERRORCODE._SUCCESS:
            logger.info(f"[+] Make 5 titles about {theme_name} complete!!")

    def button_request_proc(self):
        self.slack_bot.sendApproveMsg(self.get_theme(), self.title)
        
        evt.wait()
        evt.clear()
        if button_que.empty() == False:
            bt_type = button_que.get()
            if bt_type == config['CONF']['APPROVE_ACT_VAL']:
                logger.info("[+] User approve to post...")
                return ERRORCODE._BT_APPROVE
            elif bt_type == config['CONF']['DENY_ACT_VAL']:
                logger.info("[+] User deny to post...")
                return ERRORCODE._BT_DENY
            else:
                return ERRORCODE._BT_INVALID
        else:
            logger.info("[-] Button Queue is empty...")

    def post_blog(self):
        try:
            blog_contents = ""
            file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], self.title, "post_text"])
            with open(file_path, 'r') as con_f:
                for line in con_f.readlines():
                    if line.find("제목") != -1:             # title line remove
                        continue
                    blog_contents += "<p>"                  # tistory understand "\n" to "<p></p>"
                    blog_contents += line
                    blog_contents += "</p>"

                cate_id = self.blog_bot.getCategoryID()
                if type(cate_id) is dict:
                    if self.theme in cate_id.keys():
                        return self.blog_bot.writeBlogPost(blog_contents, 
                                                            self.title,
                                                            cate_id[self.theme])
                    else:
                       logger.info("[-] Not exist category id...")
                else:
                    logger.info("[-] Category id is not dict")
        except Exception as e:
            logger.error("post_blog funcing exception: {0}".format(e)) 
                    

    def run(self):
        logger.info("[+] ChatBlog Agent run...")
        global chatblog_timeout
        while(True):
            if chatblog_timeout:              # slack slash command or timer timeout
                evt.clear()
                chatblog_timeout = False
                if self.theme_exist_chk() == ERRORCODE._THEME_FILE_EXIST:       # exist the theme file before creating
                    self.title = self.get_usable_title()
                    if self.title == ERRORCODE._TITLE_ALL_USED:
                        self.input_request_proc()
                        evt.set()
                    else:
                        if self.button_request_proc() == ERRORCODE._BT_APPROVE:
                            res = self.gpt_bot.makeContent(self.title)
                            if type(res) is dict:
                                sub_title_list = self.gpt_bot.getSubTitle(res['response'])           # get sub titles in format list
                                self.gpt_bot.getTitleImage(sub_title_list, self.title)               # download sub titles images
                                self.gpt_bot.titleStatusUpdate(self.theme)
                                blog_url = self.post_blog()
                                self.slack_bot.sendPostMsg(self.theme,
                                                        self.title,
                                                        res['token'],
                                                        res['price'],
                                                        blog_url)
                        else:
                            # wait other request
                            pass
                else:
                    self.input_request_proc()
                    evt.set()
    def set_theme(self, theme):
        self.theme = theme

    def get_theme(self):
        return self.theme
    


async def getBody(request: Request):
    # get body from webhook request
    parse_request_body = await request.body()
    # convert bytes data to string data and decode
    parse_request_body= parse.unquote(parse_request_body.decode('utf-8')).replace("payload=", "").replace("+", " ")
    try:
        # convert str to json type
        conv_request_body = json.loads(parse_request_body)
    except Exception as e:
        parse_url = {}
        for data in parse_request_body.split("&"):
            tmp = data.split("=")
            parse_url[tmp[0]] = tmp[1]
        return parse_url
    return conv_request_body

        
@app.get("/")
async def get_test():
    return {"message" : "Hello world"}

# Request post operation
@app.post("/webhook", status_code=200)
async def webhook(request: Request):
    try:
        global chatblog_timeout
        web_t = webTool()
        header = web_t.getHeader(request)
        parm = web_t.getParm(request)
        body = await getBody(request)

        try:
            bchk = web_t.bodyCheck(body)
            if  bchk == ERRORCODE._BODY_ACT_BUTTON:
                act_val = web_t.getActVal(body)
                if act_val == config['CONF']['APPROVE_ACT_VAL']:
                    logger.info("[+] Approve button enter...")
                    try:
                        button_que.put(act_val)
                    except Exception as e:
                        logger.error(e)
                    evt.set()
                elif act_val == config['CONF']['DENY_ACT_VAL']:
                    logger.info("[+] Deny button enter...")
                    try:
                        button_que.put(act_val)
                    except Exception as e:
                        logger.error(e)
                    evt.set()
                elif act_val == config['CONF']['URL_ACT_VAL']:
                    logger.info("[+] Go to URL button enter...")
                else:
                    logger.info("action value not found")

                return {"status": "OK"}
            elif bchk == ERRORCODE._BODY_ACT_INPUT:
                logger.info("[+] Input data enter...")
                # logger.info(web_t.getActVal(body))
                try:
                    input_que.put(web_t.getActVal(body))
                except Exception as e:
                    logger.error(e)
                evt.set()

                return {"status": "OK"}
            elif bchk == ERRORCODE._BODY_CHK_CMD:
                logger.info("[+] Slash command enter...")
                try:
                    slash_que.put(body.get('text'))
                except Exception as e:
                    logger.error(e)
                # evt.set()
                chatblog_timeout = True

                return {"status": "OK"}
            elif bchk == ERRORCODE._BODY_ACT_SELECT:
                logger.info("[+] Theme select request enter...")
                # logger.info(web_t.getSelVal(body))
                try:
                    input_que.put(web_t.getSelVal(body))
                except Exception as e:
                    logger.error(e)
                evt.set()
        except Exception as e:
            logger.error(body)
            return {"status": "body structure error"}
        

    except Exception as err:
        logging.error(f'could not print REQUEST: {err}')
        return {"status": "ERR"}

def web_th():
    logger.info("[+] Web site run...")
    uvicorn.run(app, host="0.0.0.0", port=8888)

def scheduler_th():
    logger.info("[+] Scheduler run...")
    def scheduler_timeout():
        global chatblog_timeout
        chatblog_timeout = True

    schedule.every().day.at("08:30").do(scheduler_timeout)
    while(True):
        schedule.run_pending()
        time.sleep(10)

if __name__ == '__main__':
    chat_blog = chatBlog()
    
    th_web = threading.Thread(target=web_th)
    th_chat_blog = threading.Thread(target=chat_blog.run)
    th_scheduler = threading.Thread(target=scheduler_th)

    th_web.start()
    th_chat_blog.start()
    th_scheduler.start()

    
    