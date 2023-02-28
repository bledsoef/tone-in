# toneIn
This app was created in 24 hours at the Revolution UC Hackathon sponsored by Major League Hacking where it won first place. Learn more about our submission and view a demo of our application here https://devpost.com/software/tone-in.

## What It Is Used For
toneIn is a Slack application that uses machine learning and data collection to educate users on the tone of their work and personal environments. By analyzing the tone of each message in a channel using OpenAI's "davinci" model, toneIn provides users with real-time feedback on their message's formality and professionalism. It also measures each message against an overall channel tone or a tone value assigned by an administrator to ensure consistency and alert you when a message you sent may not meet the level of formality in the channel.

## Using it
If you would like to use this project yourself the first step is to make a Slack Application which can be outlined here https://api.slack.com/start/building/bolt-python.

In order to use the application you will need to create an account with OpenAI's API and Slack's API to generate API keys to allow for usage. These will be added into a .env file with the names you can find in our code.

Once an app has been made, with all the necessary keys and tokens pasted into the .env file the next thing to do is to set your applications permissions to allow it to access the proper events and have the proper scopes. The needed event handlers, slash commands and scopes will be included below:

### Slash Commands

![Screenshot_20230228_144608](https://user-images.githubusercontent.com/89262886/221962510-0a93580d-e157-411a-98f7-69f0ee6bdc99.png)

### Event Handlers

![Screenshot_20230228_144803](https://user-images.githubusercontent.com/89262886/221963001-c4868a99-b597-431e-9de1-edb6d06afc58.png)

### Scopes

![Screenshot_20230228_145115](https://user-images.githubusercontent.com/89262886/221963528-19cdc22b-b588-4002-baa0-90afb9082d68.png)

That should be all you need to know, if you have any questions feel free to reach me at bledsoef@berea.edu!
