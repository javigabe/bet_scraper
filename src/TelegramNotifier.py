#!/usr/bin/env

import telebot
import threading
import logging
import time

class TelegramNotifier(threading.Thread):
    def __init__(self, chat_id, token):
        threading.Thread.__init__(self)
        self.chat_id = chat_id
        self.bot = telebot.TeleBot(token=token)
        print(self.bot.get_me())


    def get_messages(self):
        with open ("telegram_comments.txt", "r") as myfile:
            messages = myfile.readlines()
        with open("telegram_comments.txt", "w"):
            pass
        return messages

    def run(self):
        print('We have logged in at Telegram Notifier')
        prev_messages = []

        while True:
            print("Se vuelven a buscar mensajes en Telegram")
            self.bot.send_message(-431274553, "EJECUTA DE NUEVO")
            try:
                messages = self.get_messages()
                new_messages = list(set(messages) - set(prev_messages))

                for message in new_messages:
                    self.bot.send_message(self.chat_id, message)


                prev_messages = messages
                time.sleep(300)

            except Exception as e:
                logging.error("Error en run de TelegramNotifier {}".format(e))
                time.sleep(300)
