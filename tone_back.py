import os
import openai
from dotenv import load_dotenv
import re
import pandas as pd
import matplotlib.pyplot as plt

load_dotenv()

# Load your API key from an environment variable or secret management service
class AI:
    def __init__(self):
        openai.api_key = os.getenv("API_KEY")
        self.model = "text-davinci-003"
        self.temp = .4
        self.max_token = 200

    def getRating(self, message):
        prompt = "Rate this slack text from 0-20 on professionalism on tone and vocabulary, and only tell me the " \
                 "number, no words!:" + message
        response = openai.Completion.create(model=self.model, max_tokens=self.max_token, prompt=prompt,
                                            temperature=.2)
        return response.choices[0].text

    def getSummary(self, allChatText):
        prompt = 'Provide a brief summary for the following chats with people names included.  : \n'
        for chat in allChatText:
            prompt += chat + '\n'
        response = openai.Completion.create(model='text-davinci-003', max_tokens=400, prompt=prompt, temperature=.7)
        return response.choices[0].text


class TextAnalysis:
    def __init__(self, listOfMessages, purpose):
        self.purpose = purpose
        self.listOfMessages = self.parseMessage(listOfMessages)
        self.total = 0
        self.engine = AI()
        self.scores = {}
        self.chatcount = {}
        self.converted_dict = {}
        self.tone = []
        self.average = self.analyzeMessages()

        # Model for tone analysis

        self.tone_dict = {"nonchalant": "This type of language and tone in this chat is not appropriate for"
                                        " a professional setting",
                          "very casual": "Conversations in this chat may include jokes, and sarcastic comments that "
                                         "are not very appropriate for professional setting",
                          "casual": "Participants in the chat may use informal language which may or not be"
                                    "suitable for a professional setting",
                          "professional": "The tone of this chat is appropriate "
                                          "for a professional or academic setting.",
                          "very professional": "This chat exhibits a highly professional tone and follows "
                                               "strong ethical communication suitable for a professional setting."}

    def analyzeMessages(self):

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
                for pos, char in enumerate(resp):
                    if char.isdigit():
                        splace = pos
                        break
                self.total += int(resp[splace:])

        average = self.total // (len(self.listOfMessages))
        return int(average * .90)

    def is_unprofessional(self, message):
        new_rating = self.engine.getRating(message)
        if new_rating > self.tone[0]:
            return False
        return True

    def ranking(self, order):
        self.analyzeMessages()
        for user in self.scores:
            self.scores[user] = round((self.scores[user] / (20 * self.chatcount[user])) * 100)
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True if order == "ascending" else False)
        self.converted_dict = dict(sorted_scores)
        return self.converted_dict

    def draw_rank(self, cend="descending", num=3):
        self.ranking(cend)
        # Calculate rank based on percentage score
        rank = pd.Series(list(self.converted_dict.values())).rank(method='min',
                                                                  ascending=False if cend == "ascending" else True
                                                                  ).astype(int).apply(lambda
                                                                                          x: f'{x}{["st", "nd", "rd"][x % 10 - 1] if x % 100 not in [11, 12, 13] and x % 10 in [1, 2, 3] else "th"}')
        if cend == "descending":
            rank = rank[::-1]
        # Create DataFrame
        df = pd.DataFrame(
            {'Name': list(self.converted_dict.keys()),
             'Percentage Score': [f'{score}%' for score in self.converted_dict.values()], 'Rank': rank})

        # Export to Excel
        writer = pd.ExcelWriter('rank.xlsx', engine='xlsxwriter')
        df.head(num).to_excel(writer, sheet_name='Sheet1', index=False)

        # Set column widths
        worksheet = writer.sheets['Sheet1']
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 10)

        # Set column titles and formatting
        header_format = writer.book.add_format(
            {'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9D9D9'})
        worksheet.write('A1', 'Name', header_format)
        worksheet.write('B1', 'Percentage Score', header_format)
        worksheet.write('C1', 'Rank', header_format)

        # Save and close the workbook
        writer.close()

    def draw_graph(self,  cend="descending", num=3):

        self.ranking(cend)
        rank = pd.Series(list(self.converted_dict.values())).rank(method='min',
                                                                  ascending=False if cend == "ascending" else True
                                                                  ).astype(int).apply(lambda
                                                                                          x: f'{x}{["st", "nd", "rd"][x % 10 - 1] if x % 100 not in [11, 12, 13] and x % 10 in [1, 2, 3] else "th"}')
        if cend == "descending":
            rank = rank[::-1]
        df = pd.DataFrame(
            {'Name': list(self.converted_dict.keys()),
             'Percentage Score': [f'{score}%' for score in self.converted_dict.values()], 'Rank': rank})
        # Set style
        plt.style.use('ggplot')

        # Set the slack colors for the bars
        colors = ["#36C5F0", '#E01E5A', '#ECB22E', '#2EB67D']

        # Plot horizontal bar graph
        fig, ax = plt.subplots()
        ax.bar(df['Name'], df['Percentage Score'], align='center', color = colors)

        # Set x and y labels and title
        ax.set_xlabel('Percentage Score')
        ax.set_ylabel('Name')
        ax.set_title('Leader Board')

        # Show the plot
        plt.savefig('rank.png')
        plt.show()


    def parseMessage(self, oldmessage):

        new_slack_message = []
        for array in oldmessage:
            key = array[0]
            value = array[1]

            if self.purpose == 'tone':
                if not (key.endswith('has joined the channel') or key.endswith('has been added to the channel')):
                    new_slack_message.append(key)
            else:
                new_slack_message.append(value + ':' + key)

        return new_slack_message

    def summaryResponse(self):
        return self.engine.getSummary(self.listOfMessages)

    def toneResponse(self):
        tone_average = self.analyzeMessages()
        print('I went here', tone_average)
        # print('REAL',tone_average)

        if tone_average in [0, 1, 2]:
            self.tone = [0, 1, 2]
            return self.tone_dict["nonchalant"]
        if tone_average in [3, 4, 5, 6]:
            self.tone = [3, 4, 5, 6]
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

    tone = TextAnalysis(slack_list, "summary")
    # tone = TextAnalysis(slack_list, "leaderboard")
    # print('response:', tone.toneResponse())
    # print('average:', tone.average)
    tone.draw_rank()
    tone.draw_graph()
    # print(ai.getSummary(tone.parseMessage(slack_list)))

main()
