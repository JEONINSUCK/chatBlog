from fastapi import FastAPI, Header, Request, Response
from pydantic import BaseModel
from urllib import parse

import datetime
import logging
import json
import enum


APP_NAME = "webhook-listener"
WEBHOOK_SECRET = "slackers"

# load config.json data
with open("./config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

class errorCode(enum.Enum):
    SUCCESS = enum.auto()
    BODY_CHK_OK = enum.auto()
    BODY_CHK_FAIL = enum.auto()

# log module init
logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
file_logging = logging.FileHandler(f"{APP_NAME}.log")
file_logging.setFormatter(formatter)
logger.addHandler(file_logging)

def bodyCheck(body_request):
    try:
        # load the body data form
        with open("src/message_form/webhook_req_body_form.json", 'r', encoding="utf-8-sig") as bd_f:
            form_data = json.load(bd_f)

            # get key lists
            form_keys = form_data.keys()
            body_keys = body_request.keys()

            if form_keys == body_keys:
                return errorCode.BODY_CHK_OK.value
            else:
                return errorCode.BODY_CHK_FAIL.value
            
            return 0
    except Exception as err:
        print(f"bodyCheck error: {err}")

def getMsgTheme(body: dict):
    return body['message']['attachments'][0]['blocks'][1]['fields'][0]['text'].replace('*Theme:*',"")

def getMsgTitle(body: dict):
    return body['message']['attachments'][0]['blocks'][1]['fields'][1]['text'].replace('*Title:*',"")

def getMsgDate(body: dict):
    return body['message']['attachments'][0]['blocks'][1]['fields'][2]['text'].replace('*Date:*',"")

def getMsgTime(body: dict):
    return body['message']['attachments'][0]['blocks'][1]['fields'][3]['text'].replace('*Time:*',"")

def getActVal(body: dict):
    return body['actions'][0]['value']

def getHeader(request: Request):
    return dict(request.headers.items())


def getParm(request: Request):
    return dict(request.query_params.items())


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


app = FastAPI()

@app.get("/")
async def get_test():
    return {"message" : "Hello world"}

# Request post operation
@app.post("/webhook", status_code=200)
async def webhook(request: Request):
    try:
        header = getHeader(request)
        parm = getParm(request)
        body = await getBody(request)

        if bodyCheck(body) == errorCode.BODY_CHK_OK.value:
            # await print_request(request)
            try:
                act_val = getActVal(body)
                if act_val == config['CONF']['APPROVE_ACT_VAL']:
                    print("approve button")
                    print(getMsgTheme(body))
                    print(getMsgTitle(body))
                    print(getMsgDate(body))
                    print(getMsgTime(body))
                elif act_val == config['CONF']['DENY_ACT_VAL']:
                    print("deny button")
                elif act_val == config['CONF']['INPUT']:
                    print("input button")
                else:
                    print("action value not found")

                return {"status": "OK"}
            except Exception as e:
                return {"status": "body structure error"}
        

    except Exception as err:
        logging.error(f'could not print REQUEST: {err}')
        return {"status": "ERR"}
