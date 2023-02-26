import os
import openai
from dotenv import load_dotenv
import re

load_dotenv()


# Load your API key from an environment variable or secret management service
class AI:
    def __init__(self):
        openai.api_key = os.getenv("API_KEY")
        self.model = "text-davinci-003"
        self.temp = .4
        self.max_token = 200



    def getRating(self, message):
        prompt = "Rate this slack text from 0-20 on professionalism on tone and vocabulary, and only tell me the number, no words!:" + message
        response = openai.Completion.create(model=self.model, max_tokens=self.max_token, prompt=prompt,
                                            temperature=.2)
        for result in response.choices:
            res = result.text.replace('\n','')
            # print('prompts:',message,": results",res)
            
            
            return result.text


    def getSummary(self, allChatText):
        prompt = 'Provide a brief summary for the following chats with people names included.  : \n'
        for chat in allChatText:
            prompt += chat + '\n'
            # print(prompt)

        response = openai.Completion.create(model='text-davinci-003',max_tokens=200,prompt=prompt, temperature=.7)

        # print(response.choices[0].text)
        return response.choices[0].text
    
    def suggestAppropiate(self, old_message):
        prompt = 'Can you turn this into a more professional message:' + old_message

        response = openai.Completion.create(model=self.model, max_tokens=40, prompt=prompt,
                                            temperature=.7)

        return response.choices[0].text



class TextAnalysis:
    def __init__(self, listOfMessages,purpose):
        self.purpose = purpose
        self.listOfMessages = self.parseMessage(listOfMessages)
        # print("\tAfter Parse:\n",self.listOfMessages)
        self.total = 0
        self.engine = AI()
        self.scores = {}
        self.chatcount = {}
        self.converted_dict = {}
        self.tone = []
        # self.average = self.analyzeMessages()

        # Model for tone analysis

        self.tone_dict = {"nonchalant": "This type of language and tone in this chat is not appropriate for"
                                        " a professional or academic setting, and could be "
                                        " as personal, sarcastic or even confrontational. ",
                          "very casual": "Conversations in this chat may include personal anecdotes,"
                                         " jokes, and sarcastic comments that are "
                                         "not meant to be taken seriously. May include some offensive "
                                         "language",
                          "casual": "The tone of this chat is often playful and "
                                    "may include jokes, memes, and GIFs. "
                                    "Participants in the chat may use informal language and "
                                    "emojis to express themselves.",
                          "professional": "The tone of this chat is appropriate "
                                          "for a professional or academic setting.",
                          "very professional": "The tone is helpful and informative, "
                                               "without any unnecessary or offensive language."
                                               " Overall, the tone of this chat is appropriate for "
                                               "a professional or customer service setting."}

    def analyzeMessages(self):
        # print('\tin analyze:\n' ,self.listOfMessages)
        for message in self.listOfMessages:
            resp = self.engine.getRating(message)
            try:
                self.total += int(resp)
                user = str(message.split(':')[0])
                if user not in self.scores:
                    self.scores[user] = int(resp)
                    self.chatcount[user] = 1
                else:
                    self.scores[user] = self.scores[user] + int(resp)
                    self.chatcount[user] += 1

            except:
                # print('BAD AI')
                splace = 0
                for pos,char in enumerate(resp):
                    if char.isdigit():
                       splace = pos 
                       break
                self.total += int(resp[splace:])
                # print(resp[splace:])

        average = self.total // (len(self.listOfMessages))
        # self.rank(self.scores, self.chatcount)
        # self.rank(self.scores, self.chatcount)
        return int(average*.90)

    def is_unprofessional(self, message):
        new_rating = self.engine.getRating(message)
        if int(new_rating) > self.tone[0]:
            return False
        return True
    
    def summaryResponse(self):
        return self.engine.getSummary(self.listOfMessages)
        

    def rank(self, order):
        self.analyzeMessages()
        for user in self.scores:
            self.scores[user] = round((self.scores[user]/(20 * self.chatcount[user]))*100)
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse = True if order == "ascending" else False)
        self.converted_dict = dict(sorted_scores)
        return self.converted_dict

    def draw_rank(self, cend="ascending"):
        self.rank(cend)
        message = ""
        for i in self.converted_dict.items():
            message+=("%s\t\t%s" % (i[0], i[1])+"\n")
        return message

    def parseMessage(self,oldmessage):
        
        new_slack_message = []
        for array in oldmessage:
            key = array[0]
            value = array[1]
            if self.purpose == 'tone':
                if not (key.endswith('has joined the channel') or key.endswith('has been added to the channel')):
                    new_slack_message.append(key)
            else:
                new_slack_message.append(value+':'+key)
        # print(new_slack_message)
        return new_slack_message

    def edit_professional(self,message):
        print('channel tone',self.toneResponse)
        return self.engine.suggestAppropiate(message)
        
    def toneResponse(self):
        tone_average = self.analyzeMessages()
        # print('REAL',tone_average)

        if tone_average in [0, 1, 2]:
            self.tone = [0, 1, 2]
            return self.tone_dict["nonchalant"]
        if tone_average in [3,4, 5, 6]:
            self.tone = [3,4, 5, 6]
            return self.tone_dict["very casual"]
        if tone_average in [7, 8, 9, 10]:
            self.tone = [7, 8, 9, 10]
            return self.tone_dict["casual"]
        if tone_average in [11, 12, 13, 14, 15]:
            self.tone = [11, 12, 13, 14, 15]
            return self.tone_dict["professional"]
        if tone_average in [16, 17, 18, 19, 20]:
            self.tone = [16, 17, 18, 19, 20]
            return self.tone_dict["very professional"]

# def main():
#     ai = AI()
#     slack_list = [["<@U04RC8WT7BN>Yo whats up yall", "John"],
#                   ["I won’t be in lab tomorrow <@U04RC8WT7BN>because I have dance rehearsals and I have informed my "
#                    "class that I will be on Monday night instead.", "John"],
#                   ["Yo, whats up yall?<@U04RC8WT7BN>", "Gina"],
#                   ["Yo, whats up yall!", "Gina"],
#                   ["Hi and good afternoon, everyone. Are lab hours scheduled for Sunday March 5?", "Nate"],
#                   ["What up bitches.<@U04RC8WT7BN>", "Nate"],
#                   ["Hi and good afternoon, "
#                    "everyone. Are lab hours scheduled for Sunday March 5 bitches?", "Ben"],
#                   ["Howdy People?<@U04RC8WT7BN>", "Ben"],
#                   ["howdy people?", "Ben"]]

#     tone = TextAnalysis(slack_list, "leaderboard")

#     tone.draw_rank()
#     print(tone.average)
#     print(tone.toneResponse())
#     print('average:',tone.average)
#     print(ai.getSummary(tone.parseMessage(slack_list)))
#     print(tone.toneResponse())

# main()
