import json
import requests

try:
    from common import *
except Exception as e:
    from src.common import *

# load config.json data
with open("./config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

# # set API key & GPT model
notion_secret_key = config['AUTH']['NOTION_SECRET_KEY']
notion_db_id= config['AUTH']['NOTION_DB_ID']

logger = Mylogger()

class NotionBot:
    def __init__(self) -> None:
        self.notion_base_url = "https://api.notion.com/v1/databases/"
        self.notion_db_menu = []
        self.notion_db_post_reserve_time = []
        self.notion_db_post_date = []
        self.notion_db_category = []
        self.notion_db_title = []
        self.notion_db_slack_alarm = []
        self.notion_db_tag = []

    def header_set(self, secret_key, version="2022-06-28"):
        self.headers = {
            "Authorization": secret_key,
            "Accept": "application/json",
            "Notion-Version": version
        }
        
    def get_db_info(self):
        try:
            query_path=f"{self.notion_base_url}{notion_db_id}"
            response = requests.get(query_path, headers=self.headers )

            if response.status_code == 200:
                logger.info("[+] Get notion database info OK...")
                self.db_json_data = json.loads(response.text)
            
            else:
                logger.info("[-] Get notion database info FAIL...")

        except Exception as e:
            logger.error("get_db_info funcing exception: {0}".format(e))

    # TO DO
    def parse_db_info(self):
        try:
            logger.info("[+] Pasre notion database info RUN...")
            print(self.db_info['properties'].keys())
            logger.info("[+] Pasre notion database info OK...")

            logger.info("[-] Pasre notion database info FAIL...")
        except Exception as e:
            logger.error("parse_db_info funcing exception: {0}".format(e))

    def update_db_info(self):
        try:
            query_path=f"{self.notion_base_url}{notion_db_id}"
            update_db_data = self.db_json_data['properties']
            title_sample = [
                    {
                        "type": "rich_text",
                        "rich_text": {
                        "content": "test1"
                        }
                    },
                    {
                        "type": "rich_text",
                        "rich_text": {
                        "content": "test2"
                        }
                    }
                ]
            menu_sample = {
                    'id': '810f49c7-4235-4197-a02f-f52b28d1f433',
                    'name': 'test_menu1',
                    'color': 'pink',
                    'description': None
                }
            test_data = {
                "title": [
                    {
                        "text": {
                            "content": "Ever Better Reading List Title"
                        }
                    }
                ],
                '카테고리': {
                    'id': 'WImS',
                    'name': '카테고리',
                    'type': 'select',
                    'select': {
                        'options': [
                        {
                            'id': 'f076bdfd-dee1-4786-a1e1-2b24491f19d9',
                            'name': '건강',
                            'color': 'blue',
                            'description': None
                        }
                        ]
                    }
                    }
            }
            
            update_db_data['제목']['title'] = title_sample
            update_db_data['메뉴']['select']['options'].append(menu_sample)
        
            response = requests.patch(query_path, headers=self.headers, json=test_data)    
            if response.status_code == 200:
                logger.info("[+] Update notion database info OK...")
                print(json.loads(response.text))
            
            else:
                logger.info("[-] Update notion database info FAIL...")        
                print(response)
        except Exception as e:
            logger.error("parse_db_info funcing exception: {0}".format(e))


if __name__ == '__main__':
    test_bot = NotionBot()
    test_bot.header_set(notion_secret_key)
    test_bot.get_db_info()
    # print(test_bot.db_json_data)
    test_bot.update_db_info()
