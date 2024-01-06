from datetime import datetime
from googletrans import Translator

import enum
import logging
import tiktoken
import json

EXCHANGE_RATE = 1200
DEFUALT_TOKEN = 1000

# load config.json data
with open("./config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

model = config['CONF']['GPT3_MODLE']

class ERRORCODE(enum.Enum):
    _SUCCESS = 1
    _THEME_EXIST = 2
    _THEME_NOT_EXIST = 3
    _TITLE_EXIST = 4
    _TITLE_ALL_USED = 5
    _REQUEST_GET_ERR = 6
    _CATEGORY_ID_NOT_EXIST = 7
    _SEND_MSG_FAIL = 8
    _SEND_MSG_ERR = 9
    _BODY_CHK_OK = 10
    _BODY_CHK_FAIL = 11
    _BODY_ACT_BUTTON = 12
    _BODY_ACT_INPUT = 13
    _THEME_DIR_NOT_EXIST = 14
    _THEME_FILE_NOT_EXIST = 15
    _THEME_FILE_EXIST = 16
    _TITLE_USED = 17
    _BT_DENY = 18
    _BT_INVALID = 19
    _BT_APPROVE = 20
    _QUERY_RES_ERR = 21
    _QUERY_FAIL = 22
    _BODY_CHK_CMD = 23
    _BODY_ACT_SELECT = 24
    _TITLE_DUPLI_ERR = 25
    _PARAM_ERR = 26
    _NOT_MATCH = 27

class Mylogger:
    def __init__(self) -> None:
        self.log = logging.getLogger('cnu_log')
        self.formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)s] >> %(message)s')
        self.streamHandler = logging.StreamHandler()
        self.fileHandler = logging.FileHandler('./history.log')
        self.streamHandler.setFormatter(self.formatter)
        self.fileHandler.setFormatter(self.formatter)

    def info(self, data):
        self.log.handlers.clear()
        self.log.addHandler(self.streamHandler)
        self.log.addHandler(self.fileHandler)
        self.log.setLevel(level=logging.INFO)

        self.log.info(data)

    def debug(self, data):
        self.log.handlers.clear()
        self.log.addHandler(self.fileHandler)
        self.log.setLevel(level=logging.DEBUG)
        
        self.log.debug(data)

    def error(self, data):
        self.log.handlers.clear()
        self.log.addHandler(self.streamHandler)
        self.log.addHandler(self.fileHandler)
        self.log.setLevel(level=logging.INFO)

        self.log.error(data)

class translator:
    def __init__(self) -> None:
        self.translator = Translator()


    def convEN(self, koData: str) -> str:
        return self.translator.translate(koData, src='ko', dest='en')

    def convKO(self, enData: str) -> str:
        return self.translator.translate(enData, src='en', dest='ko')

class tokenUtility:
    def __init__(self):
        try:
            self.logger = Mylogger()
            self.encoding_name = tiktoken.encoding_for_model(model)
        except Exception as e:
            self.logger.error("tokenUtility __init__ funcing exception: {0}".format(e))
    
    def getTokenNum(self, query_string: str) -> int:
        try:
            self.token_integers = self.encoding_name.encode(query_string)
            self.num_tokens = len(self.token_integers)
            return self.num_tokens
        except Exception as e:
            self.logger.error("getTokenNum funcing exception: {0}".format(e))

    def calcTokenPrice(self, token_num : int) -> float:
        try:
            if model == "gpt-3.5-turbo":
                return 0.002 / DEFUALT_TOKEN * token_num * EXCHANGE_RATE
            elif model == "gpt-3.5-turbo-0301":
                return 0.002 / DEFUALT_TOKEN * token_num * EXCHANGE_RATE
            elif model == "Ada":
                return 0.004 / DEFUALT_TOKEN * token_num * EXCHANGE_RATE
            elif model == "Babbage":
                return 0.005 / DEFUALT_TOKEN * token_num * EXCHANGE_RATE
            elif model == "Curie":
                return 0.02 / DEFUALT_TOKEN * token_num * EXCHANGE_RATE
            elif model == "Davinci":
                return 0.2 / DEFUALT_TOKEN * token_num * EXCHANGE_RATE
            else:
                return -1
        except Exception as e:
            self.logger.error("calcTokenPrice funcing exception: {0}".format(e))

    def test(self):
        print(self.encoding_name)

class keyPoint:
    def __init__(self) -> None:
        pass
    
    


if __name__ == '__main__':
    Mylogger().info('info test')
    Mylogger().debug('debug test')
    Mylogger().error('error test')