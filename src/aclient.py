import os
from typing import Union  # pylint: disable=import-error
import discord
from discord import app_commands  # pylint: disable=import-error
from dotenv import load_dotenv  # pylint: disable=import-error
from revChatGPT.V1 import AsyncChatbot  # pylint: disable=import-error
from revChatGPT.V3 import Chatbot  # pylint: disable=import-error
from src import log, responses  # pylint: disable=import-error

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

logger = log.setup_logger(__name__)

config_dir = os.path.abspath(f"{__file__}/../../")
prompt_name = "system_prompt.txt"
prompt_path = os.path.join(config_dir, prompt_name)
with open(prompt_path, "r", encoding="utf-8") as f:
    prompt = f.read()


class aclient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.current_channel = None
        self.activity = discord.Activity(
            type=discord.ActivityType.listening, name="/help | /reset"
        )
        self.isPrivate = False
        self.is_replying_all = os.getenv("REPLYING_ALL")
        self.replying_all_discord_channel_id = os.getenv(
            "REPLYING_ALL_DISCORD_CHANNEL_ID"
        )
        self.openAI_API_key = os.getenv("OPENAI_API_KEY")
        self.chatgpt_access_token = os.getenv("ACCESS_TOKEN")
        self.openAI_gpt_engine = os.getenv("GPT_ENGINE")
        self.chat_model = os.getenv("CHAT_MODEL")
        self.chatbot = self.get_chatbot_model()

    def get_chatbot_model(self, prompt=prompt) -> Union[AsyncChatbot, Chatbot]:
        if self.chat_model == "GPT3":
            return Chatbot(api_key=self.openAI_API_key, engine=self.openAI_gpt_engine, system_prompt=prompt)
        elif self.chat_model == "GPT4":
            return Chatbot(api_key=self.openAI_API_key, engine=self.openAI_gpt_engine, system_prompt=prompt)
#        elif self.chat_model == "GPT4All":
#            return AsyncChatbot(api_key=self.gpt4all_API_key, engine=self.gpt4all_engine, system_prompt=prompt)

    async def send_message(self, message, user_message):
        if self.is_replying_all == "False":  # Changing to True broke this
            author = message.user.id
        else:
            author = message.author.id
        try:
            response = (f'> **{user_message}** - <@{str(author)}> \n\n')
            if self.chat_model == "GPT3":
                response = f"{response}{await responses.official_handle_response(user_message, self)}"
            elif self.chat_model == "GPT4":
                response = f"{response}{await responses.gpt4_handle_response(user_message, self)}"
            elif self.chat_model == "GPT4All":
                response = f"{response}{await responses.gpt4all_handle_response(user_message, self)}"
            char_limit = 1900
            if len(response) > char_limit:
                # Split the response into smaller chunks of no more than 1900 characters each(Discord limit is 2000 per chunk)
                if "```" in response:
                    # Split the response if the code block exists
                    parts = response.split("```")

                    for i in range(len(parts)):
                        if i % 2 == 0:  # indices that are even are not code blocks
                            if self.is_replying_all == "True":
                                await message.channel.send(parts[i])
                            else:
                                await message.followup.send(parts[i])
                        else:  # Odd-numbered parts are code blocks
                            code_block = parts[i].split("\n")
                            formatted_code_block = ""
                            for line in code_block:
                                while len(line) > char_limit:
                                    # Split the line at the 50th character
                                    formatted_code_block += line[:char_limit] + "\n"
                                    line = line[char_limit:]
                                formatted_code_block += (line + "\n")  # Add the line and seperate with new line

                            # Send the code block in a separate message
                            if len(formatted_code_block) > char_limit + 100:
                                code_block_chunks = [formatted_code_block[i : i + char_limit]
                                                for i in range(0, len(formatted_code_block), char_limit)]
                                for chunk in code_block_chunks:
                                    if self.is_replying_all == "True":
                                        await message.channel.send(f"```{chunk}```")
                                    else:
                                        await message.followup.send(f"```{chunk}```")
                            elif self.is_replying_all == "True":
                                await message.channel.send(
                                    f"```{formatted_code_block}```"
                                )
                            else:
                                await message.followup.send(
                                    f"```{formatted_code_block}```"
                                )
                else:
                    response_chunks = [
                        response[i : i + char_limit]
                            for i in range(0, len(response), char_limit)
                    ]
                    for chunk in response_chunks:
                        if self.is_replying_all == "True":
                            await message.channel.send(chunk)
                        else:
                            await message.followup.send(chunk)
            elif self.is_replying_all == "True":
                await message.channel.send(response)
            else:
                await message.followup.send(response)
        except Exception as e:
            if self.is_replying_all == "True":
                await message.channel.send(
                    f"> **Something went wrong, please try again later!** \n ```ERROR MESSAGE: {e}```"
                )
            else:
                await message.followup.send(
                    f"> **Something went wrong, please try again later!** \n ```ERROR MESSAGE: {e}```"
                )
            logger.exception(f"Error while sending message: {e}")

        async def send_start_prompt(self):
            import os.path

            config_dir = os.path.abspath(f"{__file__}/../../")
            prompt_name = "system_prompt.txt"
            prompt_path = os.path.join(config_dir, prompt_name)
            discord_channel_id = os.getenv("DISCORD_CHANNEL_ID")
            try:
                if os.path.isfile(prompt_path) and os.path.getsize(prompt_path) > 0:
                    with open(prompt_path, "r", encoding="utf-8") as f:
                        prompt = f.read()
                        if discord_channel_id:
                            logger.info(f"Send system prompt with size {len(prompt)}")
                            response = ""
                            if self.chat_model == "GPT3":
                                response = f"{response}{await responses.official_handle_response(prompt, self)}"
                            elif self.chat_model == "GPT4":
                                response = f"{response}{await responses.gpt4_handle_response(prompt, self)}"
                            elif self.chat_model == "GPT4All":
                                response = f"{response}{await responses.gpt4all_handle_response(prompt, self)}"
                            channel = self.get_channel(int(discord_channel_id))
                            await channel.send(response)
                            logger.info(f"System prompt response:{response}")
                        else:
                            logger.info(
                                "No Channel selected. Skip sending system prompt."
                            )
                else:
                    logger.info(f"No {prompt_name}. Skip sending system prompt.")
            except Exception as e:
                logger.exception(f"Error while sending system prompt: {e}")


client = aclient()
