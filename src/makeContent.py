from datetime import datetime
import requests
import urllib.request
from requests.exceptions import ConnectionError
from googletrans import Translator
# from lib.image import *
try:
    from common import *
except Exception as e:
    from src.common import *

import openai
import json
import os
import re
import time

# from sumy.summarizers.lex_rank import LexRankSummarizer

# ASSIST_QUERY_BASE = "위 글은 블로그 게시글이야. 게시글이 입력되면 부족한 부분을 구체적으로 피드백 해줘."
ASSIST_QUERY_BASE = "위 블로그 게시글에서 부족한 부분을 구체적으로 피드백 해줘. 100자 이하로 말해줘."
CATEGORY_QUERY_BASE = "{0}에 관한 블로그 게시글을 작성할거야. \
                    {1}을 주제로한 블로그 제목을 15글자 이하로 5가지 추천해 줘. \
                    전문적이면서 호기심을 자극하는 제목으로 부탁해. \
                    20대 상냥한 여자 말투로 말해줘. \
                    이모티콘도 추가해줘."
CONTENT_QUERY_BASE = "{0}에 관한 블로그 게시글을 작성할거야. {1}을 주제로한 전문적인 블로그 글을 작성하고 싶어. \
                    20대 친근한 여성의 말투로 글을 작속하고 싶어. \
                    글은 리스트 형식으로 작성 하려고 해. \
                    그리고 문단마다 '^\d+\.\s.*\.' 형태의 정규식에 맞게 명사형의 부제목도 붙이고 싶어. \
                    글자수는 1000자 정도로 작성하고 싶어. \
                    글이 구글 SEO에 맞는 글이었으면 좋겠어. \
                    다음과 같은 조건의 블로그 글을 작성해 줘."
SYSTEM_QUERY_BASE = "{0}에 관한 전문 블로거야."
SYSTEM_CONTENT_BASE = "You are a helpful assistant who is good at detailing."
# ADV_QUERY_BASE = "다음 입력될 내용은 블로그 게시글과 피드백이야. 피드백 받은 것을 바탕으로 글을 다시 작성해줘."
ADV_QUERY_BASE = "위에서 피드백 받은 것을 바탕으로 글을 다시 작성해줘. \
                 마지막에는 블로그에서 작성하는 마무리 멘트도 작성해 줘."
SUMMARIZE_SENTENSE= "위 글을 20자 이하로 요약해줘."
# load config.json data
with open("./config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

# # set API key & GPT model
open_ai_key = config['AUTH']['GPT3_API_KEY']
model = config['CONF']['GPT3_MODLE']

# # gpt-4 model setup
# open_ai_key = config['AUTH']['GPT4_API_KEY']
# model = config['CONF']['GPT4_MODLE']

logger = Mylogger()

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
                    }
                ]
                for query in querys:
                    messages.append({"role": "user", "content": query})

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

            start_time = time.time()
            # query to chatGPT model
            try:
                response = openai.ChatCompletion.create(
                    model = model,
                    messages = messages,
                    # temperature = 0.3
                    request_timeout=180
                )
            except ConnectionError:
                logger.error(e)
            end_time = time.time()

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

                logger.info("token num: {0}, token price: {1}".format(token_num, token_price))
                
                return {"response" : conv_answer, 
                        "token" : token_num,
                        "price" : token_price,
                        "time" : f"{end_time - start_time:.2f}"}
            else:
                return ERRORCODE._QUERY_RES_ERR
        
        except Exception as e:
            logger.error("querySend funcing exception: {0}".format(e))


    def makeCategory(self):
        try:
            logger.info("[+] Make title run...")
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
                logger.error("[-] Query send FAIL")
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

            logger.info(f"[+] Make title Ok..., time: {response['time']}")
            return response
        
        except Exception as e:
            logger.error("[-] Make title FAIL...")
            logger.error("makeCategory funcing exception: {0}".format(e))


    def makeContent(self, query_string: str):
        try:
            logger.info("[+] Make content run...")
            # file check
            file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], query_string, "post_text"])
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
                logger.info(f"[+] Main query receive OK..., time: {main_answer['time']}")
                
                # # feedback query
                # assist_answer = self.querySend([self.query, ASSIST_QUERY_BASE], system=SYSTEM_QUERY_BASE.format(self.theme), assistant=[main_answer['response']])
                # if type(assist_answer) is not dict:
                #     return assist_answer
                # logger.info(f"[+] Feedback query receive OK..., time: {assist_answer['time']}")
                
                # # # advanced query
                # querys = [self.query, ASSIST_QUERY_BASE, ADV_QUERY_BASE]
                # assistant = [main_answer['response'], assist_answer['response']]
                # adv_answer = self.querySend(querys=querys, system=SYSTEM_QUERY_BASE.format(self.theme), assistant=assistant)
                # if type(adv_answer) is not dict:
                #     return adv_answer
                # logger.info(f"[+] Advanced query receive OK..., time: {adv_answer['time']}")
                adv_answer = main_answer
                
            except Exception as e:
                logger.error("[-] Query send FAIL")
                logger.error("makeContent funcing exception: {0}".format(e))
                return ERRORCODE._QUERY_FAIL

            try:
                # remove unnecessary string
                sp_datas = adv_answer['response'].split('\n')
                rm_datas = ["제목:", "피드백", "SEO", "3000자", "다시 작성", "20대 여성"]
            
                for sp_data in sp_datas[:5]:
                    for rm_data in rm_datas:
                        if sp_data.find(rm_data) != -1:
                            if sp_data in sp_datas:
                                print("[+] Unnecessary string removed...")
                                sp_datas.remove(sp_data)
                    
                adv_answer['response'] = "\n".join(sp_datas)
            except Exception as e:
                logger.error("remove unnecessary string ERR")
                logger.error(e)


            # write answer to file
            with open(file_path, 'w') as f:
                f.write(adv_answer['response'])
            # assist_file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], query_string+"_assist"])
            # with open(assist_file_path, 'w') as f:
            #     f.write(assist_answer['response'])
            # adv_file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], query_string+"_adv"])
            # with open(adv_file_path, 'w') as f:
            #     f.write(adv_answer['response'])
            

            logger.info("[+] Make content Ok...")
            return adv_answer
        
        except Exception as e:
            logger.error("[-] Make content FAIL...")
            logger.error("makeContent funcing exception: {0}".format(e))

    def sumSentense(self, text):
        assist_answer = self.querySend([text, SUMMARIZE_SENTENSE])
        if type(assist_answer) is not dict:
            return assist_answer
        logger.info("[+] Summarize query receive OK...")
        return assist_answer['response']

    def makeImg(self, prompt_text: list, title):
        logger.info("[+] makeImg run...")
        logger.info(f"[+] Torch version:{torch.__version__}")
        logger.info(f"[+] Is CUDA enabled? {torch.cuda.is_available()}")
        # self.imgModule = makeImg()

        dir_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], title])
        
        try:
            for i, p_txt in enumerate(prompt_text):
                print(p_txt)
                p_txt = self.convModule.convEN(p_txt).text
                print(p_txt)
                self.imgModule.run(prompt=p_txt, path=f"{dir_path}/image_{i}")
                logger.info(f"image_{i} save successfully")
        except IndexError:
            logger.error("[-] makeImg func prompt_text is empty")
            return ERRORCODE._PARAM_ERR
        
        logger.info("[+] makeImg OK...")


    def getThemeSrc(self):
        try:
            dir_path = os.path.join(config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH'])
            return os.listdir(dir_path)
        except Exception as e:
            logger.error("[-] Get theme source FAIL")
            logger.error("getThemeSrc funcing exception: {0}".format(e)) 

    def titleStatusUpdate(self, theme):
        try:
            file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH'], theme])

            # using category title update to file
            with open(file_path, 'w') as f:
                f.write(self.write_string)
        except Exception as e:
            logger.error("[-] Update title status FAIL")
            logger.error("titleStatusUpdate funcing exception: {0}".format(e))

    def getTitleSrc(self, theme):
        try:
            logger.info("[+] Get category title run...")
            write_string = ""
            first_find = True

            # file check
            file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH'], theme])
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                logger.info("[-] Category title file not exist...")
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

                logger.info(category_title)
                logger.info("[+] Get category title OK...")
                return category_title
            
        except Exception as e:
            logger.error("[-] Get category title FAIL")
            logger.error("getTitleSrc funcing exception: {0}".format(e))                
    
    def getTitleImage(self, sub_titles, title):
        try:
            logger.info("[+] Get sub title image run...")
            access_key = config['AUTH']['UNSPLASH_ACCESS_KEY']
            count = 2

            for sub_title in sub_titles:
                conv_title = self.convModule.convEN(sub_title).text
                
                logger.info(f"Ko_title: {sub_title}, En_title: {conv_title}")
                
                url = f'https://api.unsplash.com/photos/random?count={count}&query={conv_title}&client_id={access_key}'
                # url = f'https://api.unsplash.com/photos/?per_page={per_page}&query={conv_title}&client_id={access_key}'

                response = requests.get(url)
                search_data = response.json()
                download_url = search_data.pop()['links']['download_location']
                download_url = f'{download_url}&client_id={access_key}'

                response = requests.get(download_url, allow_redirects=True)
                # logger.debug(f"Download URL: {response.json()['url']}")

                file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], title, conv_title])
                urllib.request.urlretrieve(response.json()['url'], f"{file_path}.jpg")
                logger.debug(f"Download Image: {file_path}.jpg")
            logger.info("[+] Get sub title image OK...")
        except Exception as e:
            logger.error("[-] Get sub title image FAIL")
            logger.error("getTitleImage funcing exception: {0}".format(e))

    def getSubTitle(self, contents):
        try:
            logger.info("[+] Get sub title run...")
            # matching pattern define
            pattern_pkg = ["\d+\..*?:", "\d[.].*[:]", "^\d[.].[!]", "^\d[.].[.]", "\d[:]","[*]+.", "\d+\.\s.*", "\d+\.\s.*\."]
            sub_titles = []
            sp_datas = contents.split("\n")
            for sp_data in sp_datas:
                if sp_data != '':
                    for pattern in pattern_pkg:            
                        subtitles = re.findall(pattern, sp_data)
                        if len(subtitles) != 0:
                            sub_titles.append(self.extract_korean(subtitles.pop().strip()))
                            break
            logger.info("[+] Get sub title OK...")
            logger.info(sub_titles)
            return sub_titles
        except Exception as e:
            logger.error("[-] Get sub title FAIL")
            logger.error("getSubTitle funcing exception: {0}".format(e))
    
    def extract_korean(self, text):
        korean_pattern = re.compile('[^가-힣\s]')
        return korean_pattern.sub('', text)

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
    def testquery(self, query):
        self.query = CONTENT_QUERY_BASE.format(self.theme, query) + "문단마다 부제목도 달아줘."

        # main query
        main_answer = self.querySend([self.query], system=SYSTEM_QUERY_BASE.format(self.theme))
        if type(main_answer) is not dict:
            return main_answer
        
        # remove unnecessary string
        sp_datas = main_answer['response'].split('\n\n')
        rm_datas = ["제목:", "피드백", "SEO", "3000자", "다시 작성"]
    
        for sp_data in sp_datas[:4]:
            for rm_data in rm_datas:
                if sp_data.find(rm_data) != -1:
                    if sp_data in sp_datas:
                        print("[+] Unnecessary string removed...")
                        sp_datas.remove(sp_data)
            
        main_answer['response'] = "\n".join(sp_datas)
        print(main_answer['response'])

class translator:
    def __init__(self) -> None:
        self.translator = Translator()


    def convEN(self, koData: str) -> str:
        return self.translator.translate(koData, src='ko', dest='en')

    def convKO(self, enData: str) -> str:
        return self.translator.translate(enData, src='en', dest='ko')

if __name__ == '__main__':
    test_makeContent = makeContent()
    test_tokenTool = tokenUtility()    
    
    test_makeContent.setTheme("헬스")
    # # test_makeContent.makeCategory()
    title = test_makeContent.getTitleSrc("헬스")
    test_makeContent.makeContent(title)
    # test_makeContent.testquery(title)
    # for theme in test_makeContent.getThemeSrc():
    #     if test_makeContent.getTitleSrc(theme) == ERRORCODE._TITLE_USED:
    #         print("not exist using title")

    sub_titles = []
    file_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['CONTENTS_PATH'], title, "post_text"])
    with open(file_path, 'r') as f:
        data = f.read()

        # print(test_makeContent.getSubTitle(data))
        sub_titles = test_makeContent.getSubTitle(data)
                    
        test_makeContent.getTitleImage(sub_titles, title)

    
    #     summarizer_lex = LexRankSummarizer()
    #     # Summarize using sumy LexRank
    #     summary= summarizer_lex(sp_datas[1], 2)
    #     lex_summary=""
    #     for sentence in summary:
    #         lex_summary += str(sentence)
    #     print(lex_summary)

        # test_makeContent.makeImg(sp_datas, title=title)

        # for sp_data in sp_datas[1:]:
        #     print(sp_data)
        #     print(summarize(sp_data))
    #     rm_datas = ["제목:", "피드백", "SEO", "3000자", "다시 작성"]
    #     print(title[:-5])
        
    #     for sp_data in sp_datas[:5]:
    #         for rm_data in rm_datas:
    #             if sp_data.find(rm_data) != -1:
    #                 print("find 1")
    #                 if sp_data in sp_datas:
    #                     print("find")
    #                     sp_datas.remove(sp_data)
    #                 else:
    #                     print("nop")
    #                 # sp_datas.remove(sp_data)
    #     result= "".join(sp_datas)
    #     print(result)
