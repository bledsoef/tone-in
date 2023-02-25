from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
class History:
    def __init__(self, channel, client) -> None:
        self.history = []
        self.channel_id = channel
        self.client=client

    def get_history(self):
        try:
            result = self.client.conversations_history(channel=self.channel_id, limit=100)
            for message in result["messages"]:
                self.history.append(message["text"])
        except SlackApiError as e:
            print(f"Error: {e}")


