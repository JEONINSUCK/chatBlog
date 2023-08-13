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

# ASSIST_QUERY_BASE = "위 글은 블로그 게시글이야. 게시글이 입력되면 부족한 부분을 구체적으로 피드백 해줘."
ASSIST_QUERY_BASE = "위 블로그 게시글에서 부족한 부분을 구체적으로 피드백 해줘. 100자 이하로 말해줘."
CATEGORY_QUERY_BASE = "{0}에 관한 블로그 게시글을 작성할거야. \
                    {1}을 주제로한 블로그 제목을 15글자 이하로 5가지 추천해 줘. \
                    전문적이면서 호기심을 자극하는 제목으로 부탁해. \
                    20대 상냥한 여자 말투로 말해줘. \
                    이모티콘도 추가해줘."
CONTENT_QUERY_BASE = "{0}에 관한 블로그 게시글을 작성할거야. {1}을 주제로한 전문적인 블로그 글을 작성해 줘. 20대 친근한 여성의 말투로 대답해 줘. 리스트 형식으로 작성해 줘"
SYSTEM_QUERY_BASE = "{0}에 관한 전문 블로거야."
SYSTEM_CONTENT_BASE = "You are a helpful assistant who is good at detailing."
# ADV_QUERY_BASE = "다음 입력될 내용은 블로그 게시글과 피드백이야. 피드백 받은 것을 바탕으로 글을 다시 작성해줘."
ADV_QUERY_BASE = "위에서 피드백 받은 것을 바탕으로 구글 SEO에 맞게 글을 다시 작성해줘. \
                글자수는 3000자 내외로 써줘. \
                마지막에 결론도 도출해줘. \
                게시글에 필요하지 않은 말들은 빼줘."
# load config.json data
with open("./config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

# # set API key & GPT model
open_ai_key = config['AUTH']['GPT3_API_KEY']
model = config['CONF']['GPT3_MODLE']

# gpt-4 model setup
# open_ai_key = config['AUTH']['GPT4_API_KEY']
# model = config['CONF']['GPT4_MODLE']


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

    def querySend(self, querys: list, system="", assistant=[]):
        try:
            messages = []

            if system == "":
                system_content = SYSTEM_CONTENT_BASE
            else:
                system_content = system
            
            # conv_system = self.convModule.convEN(system_content).text
            # conv_query = self.convModule.convEN(query).text

            if len(assistant) == 0:
                messages = [
                    {
                        "role": "system",
                        "content": system_content
                    },
                    {
                        "role": "user",
                        "content": querys[0]
                    },
                ]
            else:
                # conv_assistant = self.convModule.convEN(assistant).text
                if len(querys) == (len(assistant)+1):
                    messages.append({"role": "system", "content": system_content})
                    for i in range(len(assistant)):
                        messages.append({"role": "user", "content": querys[i]})
                        messages.append({"role": "assistant", "content": assistant[i]})
                    messages.append({"role": "user", "content": querys[-1]})
                else:
                    return ERRORCODE._PARAM_ERR

            # query to chatGPT model
            response = openai.ChatCompletion.create(
                model = model,
                messages = messages,
                temperature = 0.5
            )

            if 'choices' in response:
                # parse answer and translate
                conv_answer = response['choices'][0]['message']['content']
                # conv_answer = self.convModule.convKO(answer).text
                
                # calculation token num and price
                token_num = 0
                token_price = 0
                for i in range(len(querys)):
                    token_num += self.tokenTool.getTokenNum(querys[i])
                    token_price += self.tokenTool.calcTokenPrice(token_num)

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
            
            query = CATEGORY_QUERY_BASE.format(self.theme, self.theme)
            
            try:
                response = self.querySend([query], system=self.theme)
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
                    
            if os.path.exists(file_path):                # file exist check
                with open(file_path, 'r') as f:          # title duplication check
                    write_str_list = write_string.split("\n")
                    write_string = ""
                    tmp_data = f.read()
                    for cmp_string in write_str_list:
                        re_obj = re.compile("^\d[.]")
                        if re_obj.search(cmp_string) != None:
                            if tmp_data.find(cmp_string) != -1:
                                continue
                            write_string += (cmp_string + "\n")

            with open(file_path, 'a') as f:
                f.write(write_string)

            debugPrint("[+] Make title Ok...")
            return response
        
        except Exception as e:
            debugPrint("[-] Make title FAIL...")
            debugPrint("makeCategory funcing exception: {0}".format(e))


    def makeContent(self, query_string: str):
        try:
            debugPrint("[+] Make content run...")
            # file check
            file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], query_string])
            dir_path = os.path.dirname(file_path)

            # directory check
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            self.query = CONTENT_QUERY_BASE.format(self.theme, query_string)
            
            try:
                # assist_file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], query_string+"_assist"])
                # with open(file_path, 'r') as f:
                #     main_answer = f.read()
                # with open(assist_file_path, 'r') as f:
                #     assist_answer = f.read()
    
                # main query
                main_answer = self.querySend([self.query], system=SYSTEM_QUERY_BASE.format(self.theme))
                if type(main_answer) is not dict:
                    return main_answer
                debugPrint("[+] Main query receive OK...")
                
                # feedback query
                assist_answer = self.querySend([self.query, ASSIST_QUERY_BASE], system=SYSTEM_QUERY_BASE.format(self.theme), assistant=[main_answer['response']])
                if type(assist_answer) is not dict:
                    return assist_answer
                debugPrint("[+] Feedback query receive OK...")
                
                # advanced query
                querys = [self.query, ASSIST_QUERY_BASE, ADV_QUERY_BASE]
                assistant = [main_answer['response'], assist_answer['response']]
                adv_answer = self.querySend(querys=querys, system=SYSTEM_QUERY_BASE.format(self.theme), assistant=assistant)
                if type(adv_answer) is not dict:
                    return adv_answer
                debugPrint("[+] Advanced query receive OK...")
                
            except Exception as e:
                debugPrint("[-] Query send FAIL")
                debugPrint("makeContent funcing exception: {0}".format(e))
                return ERRORCODE._QUERY_FAIL

            try:
                # remove unnecessary string
                sp_datas = adv_answer['response'].split('\n')
                rm_datas = [query_string, "피드백", "SEO", "3000자", "다시 작성"]
            
                for sp_data in sp_datas[:3]:
                    for rm_data in rm_datas:
                        if sp_data.find(rm_data) != -1:
                            sp_datas.remove(sp_data)
                adv_answer = "".join(sp_datas)
            except Exception as e:
                debugPrint("remove unnecessary string ERR")
                debugPrint(e)
                print(adv_answer)


            # write answer to file
            with open(file_path, 'w') as f:
                f.write(adv_answer['response'])
            # assist_file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], query_string+"_assist"])
            # with open(assist_file_path, 'w') as f:
            #     f.write(assist_answer['response'])
            # adv_file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], query_string+"_adv"])
            # with open(adv_file_path, 'w') as f:
            #     f.write(adv_answer['response'])
            

            debugPrint("[+] Make content Ok...")
            return adv_answer
        
        except Exception as e:
            debugPrint("[-] Make content FAIL...")
            debugPrint("makeContent funcing exception: {0}".format(e))

    def getThemeSrc(self):
        try:
            dir_path = os.path.join(config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH'])
            return os.listdir(dir_path)
        except Exception as e:
            debugPrint("[-] Get theme source FAIL")
            debugPrint("getThemeSrc funcing exception: {0}".format(e)) 

    def titleStatusUpdate(self, theme):
        try:
            file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH'], theme])

            # using category title update to file
            with open(file_path, 'w') as f:
                f.write(self.write_string)
        except Exception as e:
            debugPrint("[-] Update title status FAIL")
            debugPrint("titleStatusUpdate funcing exception: {0}".format(e))

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
            debugPrint("getTitleSrc funcing exception: {0}".format(e))                

    
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
    
    test_makeContent.setTheme("헬스")
    # # test_makeContent.makeCategory()
    title = test_makeContent.getTitleSrc("헬스")
    print(title)
    test_makeContent.makeContent(title)
    # for theme in test_makeContent.getThemeSrc():
    #     if test_makeContent.getTitleSrc(theme) == ERRORCODE._TITLE_USED:
    #         print("not exist using title")

    