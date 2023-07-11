from fastapi import FastAPI, Header, Request, Response
from pydantic import BaseModel
from uuid import UUID

import datetime
import logging

APP_NAME = "webhook-listener"
WEBHOOK_SECRET = "slackers"

app = FastAPI()

# Define reponse data
class WebhookResponse(BaseModel):
    result: str

# Define request data
class sampleData(BaseModel):
    username: str
    data: dict
    event: str
    timestamp: datetime.datetime
    model: str
    request_id: UUID

class queryStringParm(BaseModel):
    _x_id: str
    _x_csid: str
    slack_route: str
    _x_version_ts: int
    _x_frontend_build_type: str
    _x_gantry: bool
    fp: str

# Define request data
class WebhookFormData(BaseModel):
    token: str
    service_id: str
    service_team_id: str
    actions: list
    container: dict
    client_token: str
    state: dict
    _x_reason: str
    _x_mode: str
    _x_sonic: str
    _x_app_name: str


# log module init
logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
file_logging = logging.FileHandler(f"{APP_NAME}.log")
file_logging.setFormatter(formatter)
logger.addHandler(file_logging)

# log format print
def do_something_with_the_event(data):
    logger.info("WebhookData received:")
    logger.info(f"Raw data: {data}")
    logger.info(f"Request ID: {data.request_id}")
    logger.info(f"Username: {data.username}")
    logger.info(f"Event: {data.event}")
    logger.info(f"Timestamp: {data.timestamp}")
    logger.info(f"Model: {data.model}")
    logger.info(f"Data: {data.data}")
    logger.info(f"URL in data: {data.data['url']}")

@app.get("/")
async def get_test():
    return {"message" : "Hello world"}

# Request post operation
@app.post("/webhook/", response_model=WebhookResponse, status_code=200)
async def webhook(
    _x_id: str, _x_csid: str, slack_route: str, _x_version_ts: int, _x_frontend_build_type: str, _x_gantry: bool, fp: str
):
    # do_something_with_the_event(webhook_input)
    # logger.info(queryStringParm)
    return {"result": "ok"}