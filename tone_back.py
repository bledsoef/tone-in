import os
import openai
from dotenv import load_dotenv

# Load your API key from an environment variable or secret management service
class AI:
    def AI(self):
        openai.api_key = os.getenv("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")
        self.model = "text-davinci-003"
        self.temp = 1
        self.max_token = 200

    def analyzeMessage(self,message):
        prompt = "Rate from 1 to 20"
        response = openai.Completion.create(model=self.model,max_token = self.max_token,prompt=message)




    #
    # while(1>0):
    #     p = input('Enter Prompt:')
    #     response = openai.Completion.create(model="text-davinci-003", prompt=p, temperature=1, max_tokens=1000)
    #     text=response['choices'][0]['text']
    #     print(text)