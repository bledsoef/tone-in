import os
from conversations_collector import History
import logging
from slack_bolt import App  
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web import WebClient
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
def get_messages(event, client, say):
    message = event["text"]
    message_history = []
    try:
        result = client.conversations_history(channel=event["channel"], limit=100)
        for message in result["messages"]:
            message_history.append(message["text"])
    except SlackApiError as e:
        print(f"Error: {e}")
        if "tone" in message.lower():
            say("The current tone of this channel has been ")
    else:
        say("Hello!")




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