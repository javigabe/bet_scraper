#!/usr/bin/env

import discord
import threading
import time
import asyncio
import logging
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor
from launcher import Launcher
from TelegramNotifier import TelegramNotifier


client = discord.Client()
_DISCORD_TOKEN = "ODA3MzM3OTM1MDc4NTU1Njc5.YB2iCw.JUaUuGH8oxkPR4c8zwqlV-2COho"
_TELEGRAM_TOKEN = "1361997156:AAH8yT7bcwU1vpfYwbyaZ4mp2dLIiKoJN50"

def get_messages():
    with open("discord_comments.txt", "r") as myfile:
        messages = myfile.readlines()
    with open("discord_comments.txt", "w"):
        pass
    return messages


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    prev_messages = []

    while True:
        print("Se vuelven a buscar mensajes")
        try:
            loop = asyncio.get_event_loop()
            messages = await loop.run_in_executor(ThreadPoolExecutor(), get_messages)
            new_messages = list(set(messages) - set(prev_messages))

            for guild in client.guilds:
                for channel in guild.text_channels:
                    if (channel.name == 'notificador_mtos'):
                        for message in new_messages:
                            await channel.send(message)
                            #print("Se envia mensaje: " + message)

            prev_messages = messages
            await asyncio.sleep(300)

        except Exception as e:
            logging.error("Error on on_ready {}".format(e))
            await asyncio.sleep(300)



if __name__ == '__main__':
    launcher = Launcher({})
    launcher.start()
    #-431274553    CHANNEL ID
    bot = TelegramNotifier(-1001468716868, _TELEGRAM_TOKEN)
    bot.start()
    client.run(_DISCORD_TOKEN)
