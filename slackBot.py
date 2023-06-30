from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import os
import json
import enum
import requests

DEBUG_ENABLE = True

# load config.json data
with open("config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

def debugPrint(data):
    if DEBUG_ENABLE:
        print(data)


class errorCode(enum.Enum):
    SUCCESS = enum.auto()
    SEND_MSG_FAIL = enum.auto()
    SEND_MSG_ERR = enum.auto()

class Bot:
    def __init__(self) -> None:
        self.slack_token = config['AUTH']['SLACK_OAUTH_TOKEN']
        self.slack_id = config['AUTH']['SLACK_ID']
        self.slack_channel_name = config['AUTH']['SLACK_CHANNEL_NAME']
        self.slack_webhook_app_url = config['AUTH']['SLACK_WEBHOOK_APP_URL']
        self.slack_webhook_chennel_url = config['AUTH']['SLACK_WEBHOOK_APP_CHENNEL_URL']

        self.client = WebClient(token=self.slack_token)

    def sendMsg(self, msg):
        try:
            response = self.client.chat_postMessage(channel=self.slack_channel_name, \
                                                    text=msg)
            if response["ok"] is True:
                debugPrint("[+] Send message OK...")
            elif "error" in response:
                return errorCode.SEND_MSG_ERR.value
            else:
                return errorCode.SEND_MSG_FAIL.value

        except Exception as e:
            debugPrint("[-] Send message FAIL...")
            # print("getCategoryID funcing exception: {0}".format(e))

if __name__ == '__main__':
    test_Bot = Bot()
    test_Bot.sendMsg("hello")