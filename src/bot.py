import os
import discord
from random import randrange
from src.aclient import client
from discord import app_commands
from src import log, personas, responses

logger = log.setup_logger(__name__)

def run_discord_bot():
    client.is_replying_all = "True"  # Initialize client.is_replying_all to "True" if you want the Bot to reply to all comments by default

    @client.event
    async def on_ready():
        await client.send_start_prompt()
        await client.tree.sync()
        logger.info(f'{client.user} is now running!')

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
                "> **Go ahead then, get the conversation rolling**")
            logger.warning("Switch to replyAll mode")

    @client.tree.command(name="reset", description="Complete reset of the conversation history")
    async def reset(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        client.chatbot = client.get_chatbot_model()
        await client.send_start_prompt()

        client.is_replying_all = "True"
        await interaction.followup.send("> **Ahh... a new start.**")
        personas.current_persona = "standard"
        logger.warning(f"RobGPT has been successfully reset")

    @client.tree.command(name="draw", description="Generate an image with the Dalle2 model")
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

        except Exception as e:
            await interaction.followup.send(
                "> **Oops! Something went wrong**")
            logger.exception(f"Error while generating image: {e}")

    @client.tree.command(name="help", description="RobGPT, distilled")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("""\n    **BASIC COMMANDS** \n  \n
       '/switchpersona [persona]` now featuring several new personas \n
        `Robert California`: An enigma wrapped in a riddle \n
        `Lizard King`: :lizard: Pure passion and unbridled power \n
        `Sigma, Author of Dreams`: Tale Weaver \n
        `Several others`: Feedback and ideas appreciated  \n \n

       `/replyAll' toggles continuous and contextual feedback \n
       `/private` Robert will switch to private mode \n \n
       `/public` Robert will switch to public mode \n \n
       `/reset` Clear conversation history \n \n
       `Official`: Official GPT-3.5-turbo \n
       `Official-GPT4`: Official GPT-4""")

        logger.info(
            "Someone needs help!")

    @client.tree.command(name="switchpersona", description="Want to change it up a little?")
    @app_commands.choices(persona=[
        app_commands.Choice(name="Robert California", value="RobertCalifornia"),
        app_commands.Choice(name="Lizard King", value="LizardKing"),
        app_commands.Choice(name="Standard chatGPT", value="chatGPT"),
        app_commands.Choice(name="Sigma, Author of Dreams", value="sigma"),
        app_commands.Choice(name="Captain Jack Sparrow", value="JackSparrow"),
        app_commands.Choice(name="Socrates, Philosopher", value="Socrates"),
        app_commands.Choice(name="Dwight Schrute", value="DwightSchrute"),
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
            await interaction.followup.send(f"> **Youre already speaking with `{persona}`!**")

        elif persona == "standard":
            client.chatbot.reset()
            personas.current_persona = "standard"
            await interaction.followup.send(
                f"> **Switched to `{persona}`**")

        elif persona == "random":
            choices = list(personas.PERSONAS.keys())
            choice = randrange(0, 6)
            chosen_persona = choices[choice]
            personas.current_persona = chosen_persona
            await responses.switch_persona(chosen_persona, client)
            await interaction.followup.send(
                f"> **Switched to `{chosen_persona}`**")
        elif persona in personas.PERSONAS:
            try:
                await responses.switch_persona(persona, client)
                personas.current_persona = persona
                await interaction.followup.send(
                    f"> **Switched to `{persona}`**")
            except Exception as e:
                await interaction.followup.send(
                    "> **Something went wrong, please try again later! **")
                logger.exception(f"Error while switching to {e}. Try using a /reset command")

        else:
            await interaction.followup.send(
                f"> **`{persona}` doesnt want to talk, try a /reset! **")
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
                logger.exception("Error, please use `/replyAll` again, or try a /reset.")

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

client.run(TOKEN)