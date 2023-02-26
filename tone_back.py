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
        '''
        Initializes the AI object with default values for its attributes.
        '''
        # Set OpenAI API key to value stored in the environment variable "API_KEY"
        openai.api_key = os.getenv("API_KEY")
        # Set the default model to "text-davinci-003"
        self.model = "text-davinci-003"
        # Set the default temperature to 0.4
        self.temp = 0.4
        # Set the default maximum token length to 200
        self.max_token = 200

    def getRating(self, message):
        '''
        Takes a message as input and uses the OpenAI GPT API to rate the professionalism, tone, and vocabulary of the message on a scale from 0-20.
        Returns the rating as text.
        '''
        # Construct a prompt for the API with the given message
        prompt = "Rate this slack text from 0-20 on professionalism on tone and vocabulary, and only tell me the " \
                 "number, no words!:" + message
        # Call the OpenAI API to generate a response
        response = openai.Completion.create(model=self.model, max_tokens=self.max_token, prompt=prompt,
                                            temperature=self.temp)
        # Loop through the response's choices and return the first one as text
        for result in response.choices:
            res = result.text.replace('\n','')
            # print('prompts:',message,": results",res)
            return result.text

    def getSummary(self, allChatText):
        '''
        Takes a list of chat texts as input and generates a brief summary of the chats with people names included.
        Returns the summary as text.
        '''
        # Construct a prompt for the API with all the given chat texts
        prompt = 'Provide a brief summary for the following chats with people names included.  : \n'
        for chat in allChatText:
            prompt += chat + '\n'
            # print(prompt)
        # Call the OpenAI API to generate a response
        response = openai.Completion.create(model='text-davinci-003',max_tokens=200,prompt=prompt, temperature=.7)
        # Return the first choice in the response as text
        return response.choices[0].text

    
    def suggestAppropiate(self, old_message):
        '''
        Takes a message, attached to a prompt and returns a more professional version of the message.
        '''

        # Construct a prompt for the API to transform the message into a formal statement.
        prompt = 'Can you turn this into a more professional message:' + old_message

        response = openai.Completion.create(model=self.model, max_tokens=40, prompt=prompt,
                                            temperature=.7)

        return response.choices[0].text


class TextAnalysis:
    """
    A class for performing analysis on a list of text messages.
    """

    def __init__(self, listOfMessages=None, purpose=None, override_tone=None):
        """
        Initializes an instance of TextAnalysis.

        :param listOfMessages: a list of text messages to analyze
        :param purpose: the purpose of the text messages
        :param override_tone: an override for the tone analysis
        """
        self.purpose = purpose
        self.override_tone = override_tone

        # parse the messages and store them as a list
        if listOfMessages:
            self.listOfMessages = self.parseMessage(listOfMessages)

        self.total = 0
        self.engine = AI()
        self.scores = {}
        self.chatcount = {}
        self.converted_dict = {}
        self.tone = []

        # dictionary of tone categories
        self.tone_dict = {
            "nonchalant": "This type of language and tone in this chat is not appropriate for a professional setting",
            "very casual": "Conversations in this chat may include jokes, and sarcastic comments that are not very appropriate for professional setting",
            "casual": "Participants in the chat may use informal language which may or not be suitable for a professional setting",
            "professional": "The tone of this chat is appropriate for a professional or academic setting.",
            "very professional": "This chat exhibits a highly professional tone and follows strong ethical communication suitable for a professional setting."
        }

    def parseMessage(self, messages):
        """
        Parses a list of messages to remove any leading or trailing whitespace.

        :param messages: the messages to parse
        :return: a list of parsed messages
        """
        return [message.strip() for message in messages]

    def analyzeMessages(self):
        """
        Analyzes the messages and returns the average sentiment rating.

        :return: the average sentiment rating of the messages
        """
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
                splace = 0
                for pos, char in enumerate(resp):
                    if char.isdigit():
                        splace = pos
                        break
                self.total += int(resp[splace:])

        average = self.total // (len(self.listOfMessages))
        return int(average * .90)

    def is_unprofessional(self, message):
        """
        Determines if a message is unprofessional based on its sentiment rating.

        :param message: the message to analyze
        :return: True if the message is unprofessional, False otherwise
        """
        new_rating = self.engine.getRating(message)
        if int(new_rating) >= self.tone[0]:
            return False
        return True

    def summaryResponse(self):
        """
        Generates a summary of the messages using the AI engine.

        :return: the summary of the messages
        """
        return self.engine.getSummary(self.listOfMessages)

    def getTone(self):
        """
        Returns the tone of the messages.

        :return: the tone of the messages
        """
        return self.tone

    def ranking(self, order):
        """
        Returns the order of user in either ascending or descenting

        :return: a ordered dict which is in the set order
        """
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

    def edit_professional(self, message):
        """
        This method analyzes the tone of the messages received by the chatbot and
        returns a suggested appropriate response based on the tone. It also sets
        the tone of the chatbot based on the analysis.

        Args:
            message (str): The message received by the chatbot.

        Returns:
            str: The suggested appropriate response based on the tone of the message.
        """
        print('channel tone', self.toneResponse())
        return self.engine.suggestAppropiate(message)

    def toneResponse(self):
        """
        This method analyzes the tone of the messages received by the chatbot and
        returns the tone description based on the analysis. It also sets the tone
        of the chatbot based on the analysis.

        Returns:
            str: The tone description based on the analysis.
        """
        if not self.override_tone:
            tone_average = self.analyzeMessages()

            # set the tone of the chatbot based on the analysis
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
        else:
            # set the tone of the chatbot based on the override_tone parameter
            if self.override_tone == "nonchalant":
                self.tone = [0, 1, 2]
                return self.tone_dict["nonchalant"]
            if self.override_tone == "very casual":
                self.tone = [3, 4, 5, 6]
                return self.tone_dict["very casual"]
            if self.override_tone == "casual":
                self.tone = [7, 8, 9, 10]
                return self.tone_dict["casual"]
            if self.override_tone == "professional":
                self.tone = [11, 12, 13, 14, 15]
                return self.tone_dict["professional"]
            if self.override_tone == "very professional":
                self.tone = [16, 17, 18, 19, 20]
                return self.tone_dict["very professional"]

# def main():
#     ai = AI()
#     slack_list = [["<@U04RC8WT7BN>Yo whats up yall", "John"],
#                       ["I won’t be in lab tomorrow <@U04RC8WT7BN>because I have dance rehearsals and I have informed my "
#                        "class that I will be on Monday night instead.", "John"],
#                       ["Yo, whats up yall?<@U04RC8WT7BN>", "Gina"],
#                       ["Yo, whats up yall!", "Gina"],
#                       ["Hi and good afternoon, everyone. Are lab hours scheduled for Sunday March 5?", "Nate"],
#                       ["What up bitches.<@U04RC8WT7BN>", "Nate"],
#                       ["Hi and good afternoon, "
#                        "everyone. Are lab hours scheduled for Sunday March 5 bitches?", "Ben"],
#                       ["Howdy People?<@U04RC8WT7BN>", "Ben"],
#                       ["howdy people?", "Ben"]]

#     tone = TextAnalysis(slack_list, "summary")
#     # tone = TextAnalysis(slack_list, "leaderboard")
#     # print('response:', tone.toneResponse())
#     # print('average:', tone.average)
#     tone.draw_rank()
#     tone.draw_graph()
    # print(ai.getSummary(tone.parseMessage(slack_list)))

# main()
