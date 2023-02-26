import os
import re
import logging
from slack_bolt import App  
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from slack_sdk.web import WebClient
from pathlib import Path
from tone_back import TextAnalysis
from multiprocessing import Process
from dotenv import load_dotenv
from time import sleep

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
logger = logging.getLogger(__name__)
chatA: TextAnalysis = None
app = App(
    token=os.environ["SLACK_BOT_TOKEN"],    
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

opted_out_users = []
admin_set_tones = {}
current_tone = []
tones = {"nonchalant": "This type of language and tone in this chat is not appropriate for"
                                        " a professional setting",
                          "very casual": "Conversations in this chat may include jokes, and sarcastic comments that "
                                         "are not very appropriate for professional setting",
                          "casual": "Participants in the chat may use informal language which may or not be"
                                    "suitable for a professional setting",
                          "professional": "The tone of this chat is appropriate "
                                          "for a professional or academic setting.",
                          "very professional": "This chat exhibits a highly professional tone and follows "
                                               "strong ethical communication suitable for a professional setting."}

@app.command("/leaderboard")
def get_leaderboard(command, client, ack, respond):
    ack()
    respond("Generating the leaderboard, this may take a moment...")
    history = get_message_history_with_user(client, command["channel_id"], limit=None)
    channelLeaderboard = TextAnalysis(history,'leaderboard')
    leaderboard = channelLeaderboard.draw_rank()
    respond(leaderboard)

@app.command("/off")
def opt_out(respond, client, ack, command):
    ack()
    user = command["user_id"]
    if user in opted_out_users:
        respond("Already opted out of automatic tone checking!")
        return
    opted_out_users.append(user)
    respond("You are now opted out of automatic tone checking! Use /on to opt back in.")
    
@app.command("/set_tone")
def set_tone(respond, client, ack, command):
    ack()
    admin = client.users_info(user=command["user_id"]).get("user")["is_admin"]
    if not admin:
        respond("You do not have the proper permissions to update the tone. Only admins can execute this command.")
        return
    tone = command["text"]
    if tone not in tones:
        respond("Invalid tone. Use /tone-in-help to learn more about the commands.")
        return
    
    if admin_set_tones[command["channel_id"]] == tone:
        respond("Tone is already set to " + tone)
        return 

    admin_set_tones[command["channel_id"]] = tone
    respond("Tone set to " + tone + ".")

    

@app.command("/clear_tone")
def clear_tone(respond, client, ack, command):
    ack()
    admin = client.users_info(user=command["user_id"]).get("user")["is_admin"]
    if not admin:
        respond("You do not have the proper permissions to clear the set tone. Only admins can execute this command.")
        return
    
    if not admin_set_tones[command["channel_id"]]:
        respond("No admin tone set for this channel.")
        return 

    admin_set_tones.pop(command["channel_id"])
    respond("Admin tone successfully removed!")
    


@app.command("/on")
def opt_in(respond, client, ack, command):
    ack()
    user = command["user_id"]
    if user not in opted_out_users:
        respond("Already opted in to automatic tone checking!")
        return
    opted_out_users.remove(user)
    respond("You have now opted in to recieve automatic tone checking! Use /off to opt out.")


@app.command("/summary")
def get_summary(command, client, ack, respond):
    print('Summary\n')
    ack()
    respond("Generating summary, this may take a moment...")

    history = get_message_history_with_user(client, command["channel_id"], limit=30)

    for index, item in enumerate(history):
        if command["user_name"] in item[1]:
            history = history[1:index]
            break
    chatSum = TextAnalysis(history,'summary')
    summary = chatSum.summaryResponse()  #apply some function to thus
    respond(summary)

@app.command("/tone")
def get_tone(command, client, ack, respond):
    ack()
    respond("Calculating the tone, this may take a moment...")
    history = get_message_history_with_user(client, command["channel_id"])
    if not admin_set_tones[command["channel_id"]]:
        chatA = TextAnalysis(history,'tone')
        output_Message = chatA.toneResponse()
    else:
        output_Message = tones[admin_set_tones[command["channel_id"]]]
        
    respond(str(output_Message))

# @app.command('/test')
# def 
    
@app.message("")
def on_message_sent(event, client: WebClient):
    print('Message\n')
    channel_id = event.get("channel")
    user_id = event.get("user")
    if user_id in opted_out_users:
        return
    text = event.get("text")
    history = get_message_history_with_user(client, event["channel"])
    chatA = TextAnalysis(history,'tone')
    chatA.toneResponse()
    if chatA.is_unprofessional(text):
        client.chat_postEphemeral(channel=channel_id, user=user_id, blocks={
	"blocks": [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Welcome to Revolution Channel",
				"emoji": True
			}
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "plain_text",
					"text": "1) Enter /tone-in-help to get started\n 2)yolo",
					"emoji": True
				}
			]
		}
	]
})

# @app.

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
        result = client.conversations_history(channel=channel, limit=30)
        for message in result["messages"]:
            message_history.append(message["text"])
    except SlackApiError as e:
        print(f"Error: {e}")
    return message_history

def get_message_history_with_user(client: WebClient, channel, limit=30):
    message_history = []
    try:
        result = client.conversations_history(channel=channel, limit=limit)
        messages = result["messages"]
        for message in messages:
            text = message["text"]
            if "has joined the channel" in channel:
                continue
            user_ids = re.findall(r'(<@.*?>)', text)
            if user_ids is not None:
                user_names = []
                for user_id in user_ids:
                    user_id = user_id.replace("<@", "").replace(">", "")
                    user_name = client.users_info(user=user_id).get("user")["real_name"]
                    user_names.append(user_name)
                i = 0
                for user_id in user_ids:
                    text = re.sub(user_id, user_names[i], text)
                    i += 1
            user = message["user"]
            name = client.users_info(user=user).get("user")["real_name"]
            message_history.append([text,name])
    except SlackApiError as e:
        print(e)
        print(message_history[0:4])
    return message_history

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
