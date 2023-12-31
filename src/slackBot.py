from datetime import datetime
try:
    from common import *
    from postBlog import postBlog
except Exception as e:
    from src.common import *
    from src.postBlog import postBlog
import json
import requests

logger = Mylogger()

# load config.json data
with open("config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)


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
            # data = json.dumps({
            #     'blocks' : blocks_data
            # })
            data = json.dumps(
                blocks_data
            )

            response = requests.post(
                                    url=self.slack_webhook_chennel_url, 
                                    data=data,
                                    headers=header
                                )

            if response.status_code == 200:
                logger.info("[+] Post resonse 200...")
            else:
                logger.info("[-] Response ERR: {0}...".format(response.status_code))
                return ERRORCODE._SEND_MSG_FAIL

        except Exception as e:
            logger.error("[-] Main Send function FAIL...")
            logger.error("sendMsg funcing exception: {0}".format(e))


    def sendApproveMsg(self, theme, title):
        try:
            logger.info("[+] Send approval message run...")
            # load approval message form
            with open("src/message_form/approval_msg.json", "rt") as msg_f:
                approval_msg = json.load(msg_f)

                # get date & time
                now = datetime.now()
                today = now.date().strftime("%Y-%m-%d")
                today_time = now.time().strftime("%H:%M:%S")

                # fill each data to msessage form
                data_categorys = [theme, title, today, today_time]
                for i in range(len(data_categorys)):
                    approval_msg['attachments'][0]['blocks'][1]['fields'][i]['text'] = \
                    approval_msg['attachments'][0]['blocks'][1]['fields'][i]['text'].replace("[replace]", data_categorys[i])

                self.sendMsg(approval_msg)
                logger.info("[+] Send approval OK...")
        except Exception as e:
            logger.error("[-] Send approval message FAIL...")
            logger.error("sendApproveMsg funcing exception: {0}".format(e))


    def sendPostMsg(self,theme, title, token, price, url):
        try:
            logger.info("[+] Send post message run...")
            result_post_msg = ""
            # load approval message form
            with open("src/message_form/post_msg.json", "rt") as msg_f:
                post_msg = json.load(msg_f)

                # fill each data to msessage form
                data_categorys = [theme, title, str(token)+"개", str(price)+"원"]
                parse_post_msg = post_msg['attachments'][0]['blocks'][3]['text']['text'].split('\n')
                for i in range(len(data_categorys)):
                    parse_post_msg[i] = parse_post_msg[i].replace("[replace]", data_categorys[i])
                    result_post_msg += (parse_post_msg[i] + "\n")

                post_msg['attachments'][0]['blocks'][3]['text']['text'] = result_post_msg
                post_msg['attachments'][0]['blocks'][6]['elements'][0]['url'] = url

                self.sendMsg(post_msg)
            logger.info("[+] Send post message OK...")
        except Exception as e:
            logger.error("[-] Send post message FAIL...")
            logger.error("sendPostMsg funcing exception: {0}".format(e))


    def sendInputMsg(self, theme_list=None):
        try:
            logger.info("[+] Send input message...")
            # load approval message form
            with open("src/message_form/input_msg.json", "rt") as msg_f:
                input_msg = json.load(msg_f)

                if theme_list != None:
                    # fill each data to msessage form
                    field_data = input_msg['blocks'][3]['accessory']['options']
                    # clear the icon
                    field_data.clear()
                    for theme in theme_list:
                        field_form = {
                            "text": {
							"type": "plain_text",
							"text": theme,
							"emoji": True
						},
						"value": theme
                        }
                        field_data.append(field_form)
                                
                    input_msg['blocks'][3]['accessory']['options'] = field_data
                    logger.info("[+] Send input OK...")
                logger.info("[-] Theme list empty...")
                self.sendMsg(input_msg)

        except Exception as e:
            logger.error("[-] Send input message FAIL...")
            logger.error("sendInputMsg funcing exception: {0}".format(e))


    def sendButtonMsg(self):
        logger.info("[+] Send button message...")
        # load approval message form
        with open("src/message_form/button_msg.json", "rt") as msg_f:
            button_msg = json.load(msg_f)
        
            self.sendMsg(button_msg)
            logger.info("[+] Send button OK...")


if __name__ == '__main__':
    test_Bot = Bot()
    url = config['AUTH']['TISTORY_URL']
    # test_Bot.sendMsg(theme="헬스", title="운동에 필요한 요소들")
    # test_Bot.sendApproveMsg("운동", "운동에 중요한 요소 5가지")
    # test_Bot.sendPostMsg("운동", "운동에 중요한 요소 5가지", 40, 0.14, url)
    test_Bot.sendInputMsg(postBlog().getCategoryID().keys())
    # test_Bot.sendButtonMsg()
    # print(postBlog().getCategoryID().keys())
