import os
import openai
from dotenv import load_dotenv

load_dotenv()
# Load your API key from an environment variable or secret management service
class AI:
    def __init__(self):
        openai.api_key = os.getenv("API_KEY")
        self.model = "text-davinci-003"
        self.temp = .4
        self.max_token = 200

    def getRating(self,message):
        prompt = "Rate this text from 1-20 on professionality and return only the number: "+message
        print (prompt)

        response = openai.Completion.create(model=self.model,max_tokens = self.max_token,prompt=prompt, temperature= self.temp)

        for result in response.choices:
            return result.text

class ToneAnalysis:
    def __init__(self,listOfMessages):
        self.listOfMessages = self.parseMessage(listOfMessages)
        self.total = 0
        self.average = 0
        self.engine = AI()
    def analyzeMessages(self):

        for message in self.listOfMessages:
            self.total += int(self.engine.getRating(message))
        self.average = self.total // len(self.listOfMessages)

    def parseMessage(self, slack_message):
        for message in slack_message:
            if "<@U04RC8WT7BN>" in message:
                slack_message.remove(message)
        return slack_message

def main():
    ai = AI()
    slack_list = ["Yo whats up yall",
                  "I won’t be in lab tomorrow because I have dance rehearsals and I have informed my class that I will be on Monday night instead.",
                  "Yo, whats up yall?",
                  "Yo, whats up yall!",
                  "Hi and good afternoon, everyone. Are lab hours scheduled for Sunday March 5?",
                  "What up bitches.",
                  "Rate this text from 1-20 on professionality and return only the number: Hi and good afternoon, everyone. Are lab hours scheduled for Sunday March 5 bitches?",
                  "Howdy People?",
                  "howdy people?"
                  ]
    tone = ToneAnalysis(slack_list)
    tone.analyzeMessages()
    print(tone.average)

main()