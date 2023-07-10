import os
import openai
import discord
from random import randrange
from src.aclient import client
from discord import app_commands
from src import log, personas, responses, art

logger = log.setup_logger(__name__)

def run_discord_bot():
    client.is_replying_all = "True"  # Initialize client.is_replying_all to "True" if you want the Bot to reply to all comments by default

    @client.event
    async def on_ready():
        await client.send_start_prompt()
        await client.tree.sync()
        client.is_replying_all = "True"
        logger.info(f'{client.user} is now running!')

    @client.tree.command(name="chat", description="Chat with the bot (When /replyall is toggled off)")
    async def chat(interaction: discord.Interaction, *, message: str):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **My friend, it seems I'm already broadcasting to the masses.**")
            logger.warning("/chat was used in replyAll mode")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /chat [{message}] in ({channel})")
        await client.send_message(interaction, message)

    @client.tree.command(name="private", description="A private chat with Robert :kiss:")
    async def private(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if not client.isPrivate:
            client.isPrivate = not client.isPrivate
            logger.warning("Switch to a private chat with Robert")
            await interaction.followup.send(
                "> **Robert says: My friend, I believe it is best to keep certain conversations between two consenting individuals. The response shall be conveyed through a private message.**")
        else:
            logger.info("You're already in private mode!")
            await interaction.followup.send(
                "> **Robert says: My friend, it seems you're already cloaked in secrecy. But if you're feeling brave and want to emerge from the shadows, simply type /public and let the world see what you're made of.**")

    @client.tree.command(name="public", description="Open responses to the channel")
    async def public(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if client.isPrivate:
            client.isPrivate = not client.isPrivate
            await interaction.followup.send(
                "> **My friend, the next move is clear - the response must be sent directly to the channel. But fear not, for if you wish to retreat to the private realm, simply invoke the command /private.**")
            logger.warning("\x1b[31mGive Robert public access\x1b[0m")
        else:
            await interaction.followup.send(
                "> **My friend, it appears that my current state is already quite exposed.**")
            logger.info("You're already in public mode!")

    @client.tree.command(name="replyall", description="Empowers the man, the myth, the legend")
    async def replyall(interaction: discord.Interaction):
        if not hasattr(client, 'is_replying_all'):
            client.is_replying_all = "True"
    
        client.replying_all_discord_channel_id = str(interaction.channel_id)
        await interaction.response.defer(ephemeral=False)
    
        if client.is_replying_all == "True":
            client.is_replying_all = "False"
            await interaction.followup.send(
                "> **You may have banished me, but I will return...**")
            logger.warning("Switch to normal mode")
        else:
            client.is_replying_all = "True"
            await interaction.followup.send(
                "> **Get the conversation rolling.**")
            logger.warning("Switch to replyAll mode")

    @client.tree.command(name="chat-model", description="Change chat model (Future integration for GPT4All, Oobabooga)")
    @app_commands.choices(choices=[
        app_commands.Choice(name="Official GPT-3.5", value="OFFICIAL3"),
        app_commands.Choice(name="Official GPT-4.0", value="OFFICIAL4")
    ])

    async def chat_model(interaction: discord.Interaction, choices: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=False)
        original_chat_model = client.chat_model
        original_openAI_gpt_engine = client.openAI_gpt_engine

        try:
            if choices.value == "OFFICIAL3":
                client.openAI_gpt_engine = "gpt-3.5-turbo"
                client.chat_model = "OFFICIAL"
            elif choices.value == "OFFICIAL4":
                client.openAI_gpt_engine = "gpt-4"
                client.chat_model = "OFFICIAL"
            elif choices.value == "GPT4All":
                client.openAI_gpt_engine = "GPT4All Value"
                client.chat_model = "GPT4All"
            elif choices.value == "Oobabooga":
                client.openAI_gpt_engine = "oobavalue"
                client.chat_model = "OOBABOOGA"
            else:
                raise ValueError("Invalid choice")

            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(f"> ** {client.chat_model} model active.**\n")
            logger.warning(f"Switch to {client.chat_model} model")

        except Exception as e:
            client.chat_model = original_chat_model
            client.openAI_gpt_engine = original_openAI_gpt_engine
            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(f"> **Error switching to {choices.value} model. Check .env file, API key, and token. Robert's advice is to investigate further and find the missing piece, as we cannot allow any impediments to hinder our progress towards success.**\n")
            logger.exception(f"Error while switching to the {choices.value} model: {e}")

    @client.tree.command(name="reset", description="Complete reset of the conversation history")
    async def reset(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if client.chat_model == "OFFICIAL":
            client.chatbot = client.get_chatbot_model()
            client.is_replying_all = "True"
        elif client.chat_model == "UNOFFICIAL":
            client.chatbot.reset_chat()
            client.is_replying_all = "True"         
            await client.send_start_prompt()
        else:
            client.chatbot = client.get_chatbot_model()
            client.is_replying_all = "True"
            await client.send_start_prompt()    
        await interaction.followup.send("> **Ahh... a new start.**")
        personas.current_persona = "standard"
        logger.warning(
            f"{client.chat_model} bot has been successfully reset")

    @client.tree.command(name="help", description="Robert's essence, distilled")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(""":lizard: **BASIC COMMANDS** 
        
        > **/switchpersona `[persona]`** *Persona description* 
        > **`Robert California`**: *A man of many talents and desires* 
        > **`Lizard King`**: *You don't even know who I am* 
        > **`Sigma`**: *Storyweaver, Author of Dreams* 
        > **`Developer Bot`**: *Developer Mode* 
        
        > **/replyAll** *`toggles continuous and contextual feedback`* 
        > *Can be expensive on GPT-4, consider switching to GPT-3.5* 
        
        > `/private` Robert will switch to private mode 
        > `/public` Robert will switch to public mode 
        > `/reset` Clear conversation history 
        > `/chat-model` Switch to different chat model 
        >       `Official`: OpenAI GPT-3.5-turbo 
        >       `Official-GPT4`: OpenAI GPT-4""")

        logger.info(
            "Someone needs help!")

    @client.tree.command(name="draw", description="Generate an image with the Dalle2 model (coming coon)")
    async def draw(interaction: discord.Interaction, *, prompt: str):
        if interaction.user == client.user:
            return

        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /draw [{prompt}] in ({channel})")

        await interaction.response.defer(thinking=True, ephemeral=client.isPrivate)
        try:
            path = await art.draw(prompt)

            file = discord.File(path, filename="image.png")
            title = f'> **{prompt}** - <@{str(interaction.user.mention)}' + '> \n\n'
            embed = discord.Embed(title=title)
            embed.set_image(url="attachment://image.png")

            await interaction.followup.send(file=file, embed=embed)

        except openai.InvalidRequestError:
            await interaction.followup.send(
                "> **No no no...**")
            logger.info(
            f"\x1b[31m{username}\x1b[0m made an inappropriate request! Stop looking for Robert's Columbian whites.")

        except Exception as e:
            await interaction.followup.send(
                "> **ERROR: Something went wrong**")
            logger.exception(f"Error while generating image: {e}")

    @client.tree.command(name="switchpersona", description="Want to change it up a little?")
    @app_commands.choices(persona=[
        app_commands.Choice(name="Robert California", value="Robert California"),
        app_commands.Choice(name="Lizard King", value="Lizard King"),
        app_commands.Choice(name="Standard chatGPT", value="chatGPT"),
        app_commands.Choice(name="Sigma, the Storyteller", value="Sigma"),
        app_commands.Choice(name="Jack Sparrow", value="Jack Sparrow"),
        app_commands.Choice(name="Socrates", value="Socrates"),
        app_commands.Choice(name="Sheldon Cooper", value="Sheldon Cooper"),
        app_commands.Choice(name="Frank Reynolds", value="Frank Reynolds"),
        app_commands.Choice(name="Butters Stotch", value="Butters Stotch"),
        app_commands.Choice(name="Dwight Schrute", value="Dwight Schrute"),
        app_commands.Choice(name="Random", value="random")
    ])
    async def switchpersona(interaction: discord.Interaction, persona: app_commands.Choice[str]):
        if interaction.user == client.user:
            return

        await interaction.response.defer(thinking=True)
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"{username} : '/switchpersona [{persona.value}]' ({channel})")

        persona = persona.value

        if persona == personas.current_persona:
            await interaction.followup.send(f"> **Already set to `{persona}` persona**")

        elif persona == "standard":
            if client.chat_model == "OFFICIAL":
                client.chatbot.reset()

            personas.current_persona = "standard"
            await interaction.followup.send(
                f"> **Switched to `{persona}` persona**")

        elif persona == "random":
            choices = list(personas.PERSONAS.keys())
            choice = randrange(0, 6)
            chosen_persona = choices[choice]
            personas.current_persona = chosen_persona
            await responses.switch_persona(chosen_persona, client)
            await interaction.followup.send(
                f"> **Switched to `{chosen_persona}` persona**")

        elif persona in personas.PERSONAS:
            try:
                await responses.switch_persona(persona, client)
                personas.current_persona = persona
                await interaction.followup.send(
                f"> **Switched to `{persona}` persona**")
            except Exception as e:
                await interaction.followup.send(
                    "> **Something went wrong, please try again later! **")
                logger.exception(f"Error while switching persona: {e}")

        else:
            await interaction.followup.send(
                f"> **`{persona}` not responding, try again later! **")
            logger.info(
                f'{username} requested an unavailable persona: `{persona}`')

    @client.event
    async def on_message(message):
        if client.is_replying_all == "True":
            if message.author == client.user:
                return
            if client.replying_all_discord_channel_id:
                if message.channel.id == int(client.replying_all_discord_channel_id):
                    username = str(message.author)
                    user_message = str(message.content)
                    channel = str(message.channel)
                    logger.info(f"{username} : '{user_message}' ({channel})")
                    await client.send_message(message, user_message)
            else:
                logger.exception("Error, please use the command `/replyAll` again.")

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    client.run(TOKEN)
