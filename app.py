import os
from conversations_collector import History
import logging
from slack_bolt import App  
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from slack_sdk.rtm_v2 import RTMClient
from slack_sdk.web import WebClient
from pathlib import Path
from multiprocessing import Process
from dotenv import load_dotenv
from time import sleep

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
logger = logging.getLogger(__name__)

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],    
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)
@app.command("/tone")
def mention_bot(command, client, ack, respond):
    ack()
    history = get_message_history(client, command["channel_id"])
    respond("The current tone of this channel has been " + str(history) + " recently.")


@app.event("member_joined_channel")
def user_join(event, client: WebClient, say):
    history = get_message_history(client, event["channel"])
    user_id = event["user"]
    slack_response = client.conversations_open(users=[user_id])
    channel = slack_response["channel"]
    channel_name = client.conversations_info(channel=event["channel"])["channel"]["name"]
    channel_id = channel["id"]
    client.chat_postMessage(channel=channel_id, text=f"Welcome <@{user_id}>! I saw that you just joined the channel #{channel_name} " + str(history) +". Just keep that in mind while drafting your messages!")

def get_message_history(client, channel):
    message_history = []
    try:
        result = client.conversations_history(channel=channel, limit=100)
        for message in result["messages"]:
            message_history.append(message)
    except SlackApiError as e:
        print(f"Error: {e}")
        return message_history  

def get_message_history_with_user(client:WebClient, channel):
    message_history = []
    try:
        result = client.conversations_history(channel=channel, limit=4)
        messages = result["messages"]
        for message in messages:
            text = message["text"]
            user = message["user"]
            name = client.users_info(user=user).get("user")["real_name"]
            message_history.append({text:name})
    except SlackApiError as e:
        print(message_history[0:4])
    return message_history

# users_store = {}
# def save_users(users_array):
#     for user in users_array:
#         # Key user info on their unique user ID
#         user_id = user["id"]
#         # Store the entire user object (you may not need all of the info)
#         users_store[user_id] = user

# def listen_for_status_change(app):
#     print("hi")
#     result = app.client.users_list()
#     save_users(result)
#     while True:
#         for user in users_store:
#             print(app.client.users_getPresence(user=user))



if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
