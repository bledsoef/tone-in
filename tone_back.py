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



    def getRating(self, message):
        prompt = "Rate this slack text from 0-20 on professionalism on tone and vocabulary, and only tell me the number, no words!:" + message
        response = openai.Completion.create(model=self.model, max_tokens=self.max_token, prompt=prompt,
                                            temperature=.4)
        for result in response.choices:
            print('prompts:',message,": results",result.text)
            return result.text





    def getSummary(self, allChatText):
        prompt = 'Provide a brief summary for the following chats with people names included.  : \n'
        for chat in allChatText:
            prompt += chat + '\n'

        response = openai.Completion.create(model='text-davinci-003',max_tokens=400,prompt=prompt, temperature=.7)

        for result in response.choices:

            return result.text



class TextAnalysis:
    def __init__(self, listOfMessages):
        self.listOfMessages = self.parseMessage(listOfMessages)
        self.total = 0
        self.engine = AI()
        self.scores = {}
        self.chatcount = {}
        self.converted_dict = {}
        self.average = self.analyzeMessages()

        # Model for tone analysis

        self.nonchalant = [0, 1, 2]
        self.verycasual = [3,4, 5, 6]
        self.casual = [7, 8, 9, 10]
        self.professional = [11, 12, 13, 14, 15]
        self.veryprofessional = [16, 17, 18, 19, 20]
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

        for message in self.listOfMessages:
            resp = self.engine.getRating(message)
            try:
                self.total += int(resp)
                user = str(message.split(':')[0])
                print("This is user", user)
                if user not in self.scores:
                    self.scores[user] = int(resp)
                    self.chatcount[user] = 1
                else:
                    self.scores[user] = self.scores[user] + int(resp)
                    self.chatcount[user] += 1
                print(self.scores)
                print(self.chatcount)

            except:
                print('BAD AI')
        # self.rank(self.scores, self.chatcount)
        # self.rank(self.scores, self.chatcount)
        average = self.total // len(self.listOfMessages)
        return int(average*.90)

    def rank(self, order):
        self.analyzeMessages()
        print(self.scores)
        for user in self.scores:
            self.scores[user] = round((self.scores[user]/(20 * self.chatcount[user]))*100)
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse = True if order == "ascending" else False)
        self.converted_dict = dict(sorted_scores)
        print(self.converted_dict)
        return self.converted_dict

    def draw_rank(self):
        self.rank("ascending")
        "Name\tScore"
        for i in self.converted_dict.items():
            print("%s\t\t%s" % (i[0], i[1]))


    def parseMessage(self, old_slack_message):
        new_slack_message = []
        for array in old_slack_message:
            key = array[0].replace("<@U04RC8WT7BN>", "")
            value = array[1].replace("<@U04RC8WT7BN>", "")
            new_slack_message.append(value + ":" + key)
        return new_slack_message

    def toneResponse(self):
        tone_average = self.average

        if tone_average in self.nonchalant:
            return self.tone_dict["nonchalant"]
        if tone_average in self.verycasual:
            return self.tone_dict["very casual"]
        if tone_average in self.casual:
            return self.tone_dict["casual"]
        if tone_average in self.professional:
            return self.tone_dict["professional"]
        if tone_average in self.veryprofessional:
            return self.tone_dict["very professional"]

def main():
    ai = AI()
    slack_list = [["<@U04RC8WT7BN>Yo whats up yall", "John"],
                  ["I won’t be in lab tomorrow <@U04RC8WT7BN>because I have dance rehearsals and I have informed my "
                   "class that I will be on Monday night instead.", "John"],
                  ["Yo, whats up yall?<@U04RC8WT7BN>", "Gina"],
                  ["Yo, whats up yall!", "Gina"],
                  ["Hi and good afternoon, everyone. Are lab hours scheduled for Sunday March 5?", "Nate"],
                  ["What up bitches.<@U04RC8WT7BN>", "Nate"],
                  ["Hi and good afternoon, "
                   "everyone. Are lab hours scheduled for Sunday March 5 bitches?", "Ben"],
                  ["Howdy People?<@U04RC8WT7BN>", "Ben"],
                  ["howdy people?", "Ben"]]

    tone = TextAnalysis(slack_list)

    tone.draw_rank()
    print(tone.average)
    print(tone.toneResponse())
    print('average:',tone.average)
    print(ai.getSummary(tone.parseMessage(slack_list)))
    print(tone.toneResponse())

main()
