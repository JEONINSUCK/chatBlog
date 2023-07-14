from makeContent import makeContent
from postBlog import postBlog
from slackBot import Bot
from datetime import datetime

import web_server
import os
import json
import enum


DEBUG_ENABLE = True

# load config.json data
with open("./config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

class errorCode(enum.Enum):
    SUCCESS = enum.auto()
    THEME_EXIST = enum.auto()
    THEME_DIR_NOT_EXIST = enum.auto()
    THEME_FILE_NOT_EXIST = enum.auto()
    THEME_FILE_EXIST = enum.auto()
    TITLE_EXIST = enum.auto()

def debugPrint(data):
    if DEBUG_ENABLE:
        # get date & time
        now = datetime.now()
        today = now.date().strftime("%y-%m-%d")
        today_time = now.time().strftime("%H:%M:%S")
        print("{0} {1} - ".format(today, today_time), end="")
        print(data)

# check the theme file and dir
def theme_exist_chk():
    dir_path = os.path.join(*[config['CONF']['MEMORY_PATH'], config['CONF']['TITLES_PATH']])
    # directory check
    if not os.path.exists(dir_path):
        return errorCode.THEME_DIR_NOT_EXIST.value
    # file check
    elif len(os.listdir(dir_path)) == 0:
        return errorCode.THEME_FILE_NOT_EXIST.value
    else:
        return errorCode.THEME_FILE_EXIST.value


def chatBlog_run():
    gpt_bot = makeContent()
    blog_bot = postBlog()
    slack_bot = Bot()

    if theme_exist_chk() == errorCode.THEME_FILE_EXIST.value:       # exist the theme file before creating
        if gpt_bot.getCategoryTitle() == None:          # do not have usable title
            pass
        else:
            pass
    
    else:           # do not have theme file
        slack_bot.sendInputMsg()



if __name__ == '__main__':
    chatBlog_run()