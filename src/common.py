from datetime import datetime
import enum


DEBUG_ENABLE = True

class errorCode(enum.Enum):
    SUCCESS = enum.auto()
    THEME_EXIST = enum.auto()
    THEME_NOT_EXIST = enum.auto()
    TITLE_EXIST = enum.auto()
    TITLE_ALL_USED = enum.auto()
    REQUEST_GET_ERR = enum.auto()
    CATEGORY_ID_NOT_EXIST = enum.auto()
    SEND_MSG_FAIL = enum.auto()
    SEND_MSG_ERR = enum.auto()
    BODY_CHK_OK = enum.auto()
    BODY_CHK_FAIL = enum.auto()
    BODY_ACT_BUTTON = enum.auto()
    BODY_ACT_INPUT = enum.auto()
    THEME_DIR_NOT_EXIST = enum.auto()
    THEME_FILE_NOT_EXIST = enum.auto()
    THEME_FILE_EXIST = enum.auto()
    
def debugPrint(data):
    if DEBUG_ENABLE:
        # get date & time
        now = datetime.now()
        today = now.date().strftime("%y-%m-%d")
        today_time = now.time().strftime("%H:%M:%S")
        print("{0} {1} > ".format(today, today_time), end="")
        print(data)