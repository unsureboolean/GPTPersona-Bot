from src import personas
from asgiref.sync import sync_to_async

async def official_handle_response(message, client) -> str:
    return await sync_to_async(client.chatbot.ask)(message)

# Ooba or GPT4All 
async def unofficial_handle_response(message, client) -> str:
    async for response in client.chatbot.ask(message):
        responseMessage = response["message"]
    return responseMessage

# Resets conversation and prompts the user for a new persona
async def switch_persona(persona, client) -> None:
    if client.chat_model ==  "UNOFFICIAL":
        client.chatbot.reset_chat()
        async for _ in client.chatbot.ask(personas.PERSONAS.get(persona)):
            pass
    elif client.chat_model == "OFFICIAL":
        client.chatbot = client.get_chatbot_model(prompt=personas.PERSONAS.get(persona))
    elif client.chat_model == "GPT4All":
        client.chatbot = client.get_chatbot_model()
        await sync_to_async(client.chatbot.ask)(personas.PERSONAS.get(persona))
    elif client.chat_model == "Oobabooga":
        await client.chatbot.reset()
        async for _ in client.chatbot.ask_stream(personas.PERSONAS.get(persona)):
            pass
