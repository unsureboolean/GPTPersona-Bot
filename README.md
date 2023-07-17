# GPTPersona-Bot
### Persona Impersonating Discord Bot

## Features

### Switch Persona
* Currently version is running with Butters Stotch as the default persona. More persona's can easily be added in the personas.py file. Make sure add the persona to the bot.py file by adding the name and value you've assigned *app_commands.Choice(name="Persona Name/Label", value="yourPersonaValue")*

* /switchpersona: Switch between personas
   * `Robert California`: The man himself
   * `Lizard King`: Robert, evolved
   * `Sigma`: Epic Storyteller
   * `Socrates`: The wise one?
   * `Dwight Schrute`: Beet farmer, paper salesman
   * `random`: Picks a random persona
   * `More` Frank Reynolds, Butters Stotch, Jack Sparrow

* `/private` Robert will switch to private mode
* `/public` Robert will switch to public mode
* `/replyall` Robert will reply to the masses
* `/reset` Clear conversation history
* `/chat-model` Switch to different chat model
   * `OFFICIAL-GPT-3.5`: GPT-3.5-turbo model
   * `OFFICIAL-GPT-4.0`: GPT-4.0 model should work for those who have this available, I have not tested yet



### Mode

* `public mode (default)`  GPTPersonaBot directly replies on the channel to targeted chats

* `private mode` GPTPersonaBot's reply can only be seen by the person who used the command

* `replyall mode` GPTPersonaBot will reply to all messages in the channel without using slash commands

### Chat

* `/chat` Command can be used to chat with the bot outside of replyAll mode.

### Draw

* In beta, currently working I think...


# Setup

## Prerequisites to install

* Python version `3.11` or higher required

* You need a Discord Developer account (free) at https://discord.com/build/app-developers

* You also need an OpenAI Developer account and API key (free) at https://platform.openai.com/signup

* Run ```pip3 install -r requirements.txt``` from bot's root folder in terminal

* Open "dotenv.example.txt" and rename to ".env" (no name, extension only) with your new API key and Bot token

* Adjust the .env file with your API key and Bot token (Step 1 and 2)


## Step 1: Create a Discord bot

1. Go to Discord's developer portal and create a bot (Instructions for this everywhere, it's easy)

2. Get the Discord bot's token (Store this somewhere safe)

3. In the .env file, set the token as the `DISCORD_BOT_TOKEN` variable

4. Turn on all Intents in developer portal on discord


## Step 2: Get your OpenAI API key

1. Sign up for a Developer Account on openai.com

2. Go to https://beta.openai.com/account/api-keys and get a secret API key (Store this too)

3. In the .env file, set your OpenAI API key as the `OPENAI_API_KEY` variable with no quotes or trailing lines


## Step 3: Run RobGPT on the desktop (Command line)

1. Open a terminal, command prompt, powershell, etc.

2. Navigate to the directory where you installed the bot.

3. Type `python main.py` to start the bot


### Please help by reporting bugs!

   > **Known bugs**
   > - The bot will reply to everything in replyall mode.  Make sure you turn on slowdown mode in discord because he will crash and stop responding if he gets more requests before he has answered the last one. Need an actual queue system and not the bs I patched together.
     > - When messages get queued, the bot throws an error.  The messages go through as one message usually, RobGPT throws an error, but then usually responds to both messages as if they were one prompt.
   > - The bot will occasionally forget who it is.  This is ok, it happens to all of us from time to time.  You may need to /reset or /switchpersona.
   > - ~~When changings or after a reset, Robert will exit /replyall mode but will not mention anything about it. You need to turn it off and back on to get his attention. I will adjust the message when I get time.~~ *Fixed*
     > - This introduced a bug where the bot will sometimes take longer to reply (about 20-30 seconds). Leaving it for now as it is only occasional but it needs to be investigated.
   > - At one point the bot was able to talk to multiple servers and reply independantly in each one.  At some point I lost this functionality so it will need to be reinstated.

   > **Future implementations:**
   > - Get GPTPersonaBot to change it's server nickname whenever he changes personas in that server
   > - Docker support
   > - Support for GPT4All and other LLM repositories
   > - Build in feedback command for machine learning (/feedback :thumbsup: and /feedback :thumbsdown:)
---
