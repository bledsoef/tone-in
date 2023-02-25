import os
from conversations_collector import History
import logging
from slack_bolt import App  
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
logger = logging.getLogger(__name__)

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

@app.event("app_mention")
def mention_bot(event, client, say):
    message = event["text"]
    history = get_message_history(client, event)
    if "tone" in message.lower():
        say("The current tone of this channel has been " + history + " recently.")
    else:
        say("Hello!")

@app.event("member_joined_channel")
def user_join(event, client, say):
    logger.log(logging.DEBUG, "User joined")
    history = get_message_history(client, event)
    user = event["user"]
    say(f"Welcome <@{user}>! The tone of this channel is " + str(history) +". Just keep that in mind while drafting your messages!")

def get_message_history(client, event):
    message_history = []
    try:
        result = client.conversations_history(channel=event["channel"], limit=100)
        for message in result["messages"]:
            message_history.append(message)
    except SlackApiError as e:
        print(f"Error: {e}")


# @app.event("app_home_opened")
# def update_home_tab(client, event, logger):
#   try:
#     # views.publish is the method that your app uses to push a view to the Home tab
#     client.views_publish(
#       # the user that opened your app's app home
#       user_id=event["user"],
#       # the view object that appears in the app home
#       view={
#         "type": "home",
#         "callback_id": "home_view",

#         # body of the view
#         "blocks": [
#           {
#             "type": "section",
#             "text": {
#               "type": "mrkdwn",
#               "text": "*Welcome to your _App's Home_* :tada:"
#             }
#           },
#           {
#             "type": "divider"
#           },
#           {
#             "type": "section",
#             "text": {
#               "type": "mrkdwn",
#               "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
#             }
#           },
#           {
#             "type": "actions",
#             "elements": [
#               {
#                 "type": "button",
#                 "text": {
#                   "type": "plain_text",
#                   "text": "Click me!"
#                 }
#               }
#             ]
#           }
#         ]
#       }
#     )
  
#   except Exception as e:
#     logger.error(f"Error publishing home tab: {e}")

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()