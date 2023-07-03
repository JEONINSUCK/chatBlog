from datetime import datetime

import os
import json
import enum
import requests
import re

DEBUG_ENABLE = True


# load config.json data
with open("config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

def debugPrint(data):
    if DEBUG_ENABLE:
        # get date & time
        now = datetime.now()
        today = now.date().strftime("%y-%m-%d")
        today_time = now.time().strftime("%H:%M:%S")
        print("{0} {1} > ".format(today, today_time), end="")
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
        self.slack_webhook_chennel_url = config['AUTH']['SLACK_WEBHOOK_CHENNEL_URL']


    def sendMsg(self, blocks_data):
        try:
            header = {'Content-type': 'application/json'}
            data = json.dumps({
                'blocks' : blocks_data
            })

            response = requests.post(
                                    url=self.slack_webhook_chennel_url, 
                                    data=data,
                                    headers=header
                                )

            if response.status_code == 200:
                debugPrint("[+] Send message OK...")
            else:
                debugPrint("[+] Response ERR: {0}...".format(response.status_code))
                return errorCode.SEND_MSG_FAIL.value

        except Exception as e:
            debugPrint("[-] Send message FAIL...")
            print("sendMsg funcing exception: {0}".format(e))


    def sendApproveMsg(self, theme, title):
        try:
            debugPrint("[+] Send approval message...")
            # load approval message form
            with open("approval_msg.json", "rt") as msg_f:
                approval_msg = json.load(msg_f)

                # get date & time
                now = datetime.now()
                today = now.date().strftime("%Y-%m-%d")
                today_time = now.time().strftime("%H:%M:%S")

                # fill each data to msessage form
                data_categorys = [theme, title, today, today_time]
                for i in range(len(data_categorys)):
                    approval_msg[1]['fields'][i]['text'] = \
                    approval_msg[1]['fields'][i]['text'].replace("[replace]", data_categorys[i])

                self.sendMsg(approval_msg)
        except Exception as e:
            # debugPrint("[-] Send message FAIL...")
            print("sendApproveMsg funcing exception: {0}".format(e))


    def sendPostMsg(self,theme, title, token, price):
        try:
            debugPrint("[+] Send post message...")
            result_post_msg = ""
            # load approval message form
            with open("post_msg.json", "rt") as msg_f:
                post_msg = json.load(msg_f)

                # fill each data to msessage form
                data_categorys = [theme, title, str(token)+"개", str(price)+"원"]
                parse_post_msg = post_msg[3]['text']['text'].split('\n')
                for i in range(len(data_categorys)):
                    parse_post_msg[i] = parse_post_msg[i].replace("[replace]", data_categorys[i])
                    result_post_msg += (parse_post_msg[i] + "\n")

                post_msg[3]['text']['text'] = result_post_msg

                self.sendMsg(post_msg)
        except Exception as e:
            # debugPrint("[-] Send message FAIL...")
            print("sendPostMsg funcing exception: {0}".format(e))


    def sendInputMsg(self, theme_list):
        try:
            debugPrint("[+] Send input message...")
            # load approval message form
            with open("input_msg.json", "rt") as msg_f:
                input_msg = json.load(msg_f)

                # fill each data to msessage form
                field_data = input_msg[2]['fields']
                for theme in theme_list:
                    field_form = {"type": "mrkdwn", "text": "• "+theme}
                    field_data.append(field_form)
                            
                input_msg[2]['fields'] = field_data

                self.sendMsg(input_msg)
        except Exception as e:
            # debugPrint("[-] Send message FAIL...")
            print("sendInputMsg funcing exception: {0}".format(e))

if __name__ == '__main__':
    test_Bot = Bot()
    # test_Bot.sendMsg(theme="헬스", title="운동에 필요한 요소들")
    # test_Bot.sendApproveMsg("운동", "운동에 중요한 요소 5가지")
    # test_Bot.sendPostMsg("운동", "운동에 중요한 요소 5가지", 40, 0.14)
    test_Bot.sendInputMsg(['운동', '헬스', '요리'])
