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
        self.listOfMessages = listOfMessages
        self.sum = 0
        self.average = self.sum // len(listOfMessages)
        self.engine = AI()
    def analyzeMessages(self):

        for message in self.listOfMessages:
            self.sum += self.engine.getRating(message)





def main():
    ai = AI()
    print(ai.getRating('I won’t be in lab tomorrow because I have dance rehearsals and I have informed my class that I will be on Monday night instead.'))

main()