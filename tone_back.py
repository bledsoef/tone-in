import os
import openai
from dotenv import load_dotenv


load_dotenv()
# Load your API key from an environment variable or secret management service
class AI:
    def __init__(self):
        openai.api_key = os.getenv("API_KEY")
        self.model = "text-davinci-003"
        self.temp = 0
        self.max_token = 200

    def analyzeMessage(self,message):
        prompt = "Rate this text from 1-20 on professionality and return only the number: "+message
        print (prompt)

        response = openai.Completion.create(model=self.model,max_tokens = self.max_token,prompt=prompt, temperature= self.temp)
        print(response)
        for result in response.choices:
            print(result)
            return (result.text)
        response.close()


def main():
    ai = AI()
    print(ai.analyzeMessage('what up bitches'))

main()