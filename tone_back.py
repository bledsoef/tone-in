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

        response = openai.Completion.create(model='text-davinci-003',max_tokens=400,prompt=prompt, temperature=1)

        for result in response.choices:

            return result.text



class TextAnalysis:
    def __init__(self, listOfMessages):
        self.listOfMessages = self.parseMessage(listOfMessages)
        self.total = 0
        self.engine = AI()
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
            except:
                print('BAD AI')

        print(self.total,len(self.listOfMessages))
        average = self.total // len(self.listOfMessages)
        return int(average*.90 )

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
    slack_list = ['Anish Kharel: Good morning everyone, I hope everyone had a good weekend.',
                  "Finn:But yes I think the plan was to nap on and off.",
                  "Finn :If anyone prefers otherwise, we can figure something out.",
                  "Anish Kharel:Yes,that what we did last time and it was perfectly fine.",
                  "Daize Njounkeng: Have you guys already started brainstorming idea?",
                  "Daize Njounkeng: Would you guys like to build something with Open Ai API?",
                  "Anish Kharel: Yes, that sounds like alot of fun!"

          ]

    # slack_list = ["Daize Njounkeng:Hey I reached out to Moise should hear from him this evening.",
    #               "Daize Njounkeng:Just making sure, we are going to take napsin the hackathon classrooms yes? Or we are planning on lodging somewhere.",
    #               "Finn:I think we're all just gonna get coked out and not need to sleep",
    #               "Finn:But yes I think the plan was to nap on and off.",
    #               "Finn :If anyone prefers otherwise we can figure something out.",
    #               "Slackbot:@moise dk has been added to the conversation by Daize Njounkeng.",
    #               "Anish Kharel:yes that what we did last time",
    #               "Anish Kharel:it wasn't the best but it was aight",
    #               "Daize Njounkeng: So already started brainstorming application ideas.",
    #               "Daize Njounkeng: Would you guys like to build something with Open Ai API?",
    #               "Finn: That sounds interesting, what are you thinking?",
    #               ]
    tone = TextAnalysis(slack_list)
    slack_list = [["<@U04RC8WT7BN>Yo whats up yall", "id"],
                  ["I won’t be in lab tomorrow <@U04RC8WT7BN>because I have dance rehearsals and I have informed my "
                   "class that I will be on Monday night instead.", "id"],
                  ["Yo, whats up yall?<@U04RC8WT7BN>", "id"],
                  ["Yo, whats up yall!", "id"],
                  ["Hi and good afternoon, everyone. Are lab hours scheduled for Sunday March 5?", "id"],
                  ["What up bitches.<@U04RC8WT7BN>", "id"],
                  ["Rate this text from 1-20 on professionality and return only the number: Hi and good afternoon, "
                   "everyone. Are lab hours scheduled for Sunday March 5 bitches?", "id"],
                  ["Howdy People?<@U04RC8WT7BN>", "id"],
                  ["howdy people?", "id"]]

    tone = ToneAnalysis(slack_list)
    tone.analyzeMessages()
    print(tone.average)
    print(tone.toneResponse())
    print('average:',tone.average)
    print(ai.getSummary(slack_list))
    # print(tone.toneResponse())


main()
