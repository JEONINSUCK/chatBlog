from googletrans import Translator
from datetime import datetime
try:
    from common import *
except Exception as e:
    from src.common import *

import openai
import tiktoken
import json
import os
import re

EXCHANGE_RATE = 1200
DEFUALT_TOKEN = 1000

CATEGORY_QUERY_BASE = "{0}에 관한 블로그 게시글을 작성할거야. {1}을 주제로한 카테고리 제목을 5가지 나열해 줘."
CONTENT_QUERY_BASE = "{0}에 관한 블로그 게시글을 작성할거야. {1}을 주제로 리스트 형식의 글을 작성해 줘."
SYSTEM_QUERY_BASE = "에 관한 블로거야."
SYSTEM_CONTENT_BASE = "You are a helpful assistant who is good at detailing."

# load config.json data
with open("./config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

# set API key & GPT model
open_ai_key = config['AUTH']['GPT3_API_KEY']
model = config['CONF']['GPT3_MODLE']


class makeContent:
    def __init__(self):
        self.tokenTool = tokenUtility()
        self.convModule = translator()
        openai.api_key = open_ai_key
        self.query = ""
        self.answer = ""
        self.conv_answer = ""
        self.theme = ""
        self.parse_answer = []
        self.write_string = ""

    def querySend(self, query: str, user="user", system="", assistant="") -> str:
        try:
            if system == "":
                system_content = SYSTEM_CONTENT_BASE
            else:
                system_content = system

            conv_query = self.convModule.convEN(query).text
            messages = [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user",
                    "content": conv_query
                },
            ]

            # query to chatGPT model
            response = openai.ChatCompletion.create(
                model = model,
                messages = messages
            )

            if 'choices' in response:
                # parse answer and translate
                answer = response['choices'][0]['message']['content']
                conv_answer = self.convModule.convKO(answer).text

                token_num = self.tokenTool.getTokenNum(conv_query)
                token_price = self.tokenTool.calcTokenPrice(token_num)

                debugPrint("token num: {0}, token price: {1}".format(token_num, token_price))
                
                return {"response" : conv_answer, 
                        "token" : token_num,
                        "price" : token_price}
            else:
                return ERRORCODE._QUERY_RES_ERR
        
        except Exception as e:
            print("querySend funcing exception: {0}".format(e))


    def makeCategory(self):
        try:
            debugPrint("[+] Make title run...")
            write_string = ""
            file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH'], self.theme])
            dir_path = os.path.dirname(file_path)
            # directory check
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            # # file check
            # if os.path.exists(file_path):
            #     debugPrint("[+] Titles EXIST...")
            #     return ERRORCODE._THEME_EXIST
            

            query = CATEGORY_QUERY_BASE.format(self.theme, self.theme)
            
            try:
                response = self.querySend(query)
            except Exception as e:
                debugPrint("[-] Query send FAIL")
                return ERRORCODE._QUERY_FAIL
            now = datetime.now()
            today = now.date().strftime("%Y-%m-%d")
            today_time = now.time().strftime("%H:%M:%S")
            # file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], theme, today, today_time])

            # answer parsing
            parse_responses = response['response'].split("\n")
            re_compile = re.compile("^\d[.]")
            for parse_response in parse_responses:
                if re_compile.match(parse_response) != None:
                    write_string += (parse_response + "\n")
                    
            with open(file_path, 'a') as f:
                f.write(write_string)

            debugPrint("[+] Make title Ok...")
            return response
        
        except Exception as e:
            debugPrint("[-] Make title FAIL...")
            # print("makeCategory funcing exception: {0}".format(e))


    def makeContent(self, query_string: str):
        try:
            debugPrint("[+] Make content run...")
            # file check
            file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], query_string])
            dir_path = os.path.dirname(file_path)

            # directory check
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            # file check
            if os.path.exists(file_path):
                debugPrint("[-] Make content FAIL...")
                return ERRORCODE._TITLE_EXIST
            # title duplication check
            theme_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH'], self.theme])
            with open(theme_path, 'r') as f:
                tmp_data = f.read()
                if tmp_data.find(query_string) == -1:
                    return ERRORCODE._TITLE_DUPLI_ERR
            # query = "초보자에 관련된 운동 블로그를 써줘. 가슴 운동에 관한 운동 방법에 대해 써줘. 제일 처음 제목을 써줘. 다른 운동 블로그를 참고 하여 전문적인 표현을 많이 사용해 줘"
            self.query = CONTENT_QUERY_BASE.format(self.theme, query_string)
            # self.conv_query = self.convModule.convEN(self.query).text
            
            try:
                self.conv_answer = self.querySend(self.query)
            except Exception as e:
                debugPrint("[-] Query send FAIL")
                return ERRORCODE._QUERY_FAIL
            self.parse_answer = self.conv_answer['response'].split('\n')

            # write answer to file
            with open(file_path, 'w') as f:
                f.write(self.conv_answer['response'])

            debugPrint("[+] Make content Ok...")
            return self.conv_answer
        
        except Exception as e:
            # print("makeContent funcing exception: {0}".format(e))
            debugPrint("[-] Make content FAIL...")

    def getThemeSrc(self):
        try:
            dir_path = os.path.join(config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH'])
            return os.listdir(dir_path)
        except Exception as e:
            debugPrint("[-] Get theme source FAIL")
            print("getThemeSrc funcing exception: {0}".format(e)) 

    def titleStatusUpdate(self, theme):
        try:
            file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH'], theme])

            # using category title update to file
            with open(file_path, 'w') as f:
                f.write(self.write_string)
        except Exception as e:
            debugPrint("[-] Update title status FAIL")
            print("titleStatusUpdate funcing exception: {0}".format(e))

    def getTitleSrc(self, theme):
        try:
            write_string = ""
            first_find = True

            # file check
            file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH'], theme])
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                debugPrint("[-] Category title file not exist...")
                return ERRORCODE._THEME_NOT_EXIST
            else:
                # used category title check
                with open(file_path, 'r') as f:
                    for line in f.readlines():
                        if line.find("[used]") == -1 and first_find:
                            category_title = line.split('.')
                            category_title = category_title[1].replace("\n", "").strip()

                            write_string += line.replace("\n", "\t[used]\n")

                            first_find = False
                        else:
                            write_string += line

                    if first_find == True:
                        return ERRORCODE._TITLE_USED
                    
                self.write_string = write_string

                debugPrint("[+] Get category title OK...")
                return category_title
            
        except Exception as e:
            debugPrint("[-] Get category title FAIL")
            print("getTitleSrc funcing exception: {0}".format(e))                

    
    def setTheme(self, theme):
        self.theme = theme

    def getQueryEn(self) -> str:
        return self.conv_query
    
    def getQueryKo(self) -> str:
        return self.query
    
    def getAnswerEn(self) -> str:
        return self.conv_answer

    def getAnswerKo(self) -> str:
        return self.answer

    def showModelList(self) -> list:
        i = 0
        for model_name in openai.Model.list():
            print(i)
            print(model_name)
            i += 1
        

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
            self.encoding_name = tiktoken.encoding_for_model(model)
        except Exception as e:
            print("tokenUtility __init__ funcing exception: {0}".format(e))
    
    def getTokenNum(self, query_string: str) -> int:
        try:
            self.token_integers = self.encoding_name.encode(query_string)
            self.num_tokens = len(self.token_integers)
            return self.num_tokens
        except Exception as e:
            print("getTokenNum funcing exception: {0}".format(e))

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
            print("calcTokenPrice funcing exception: {0}".format(e))

    def test(self):
        print(self.encoding_name)



if __name__ == '__main__':
    test_makeContent = makeContent()
    test_tokenTool = tokenUtility()    
    
    # test_makeContent.setTheme("헬스")
    # test_makeContent.makeCategory()
    # title = test_makeContent.getTitleSrc()
    # test_makeContent.makeContent(title)
    for theme in test_makeContent.getThemeSrc():
        if test_makeContent.getTitleSrc(theme) == ERRORCODE._TITLE_USED:
            print("not exist using title")
    
    