#!/usr/bin/env


import threading
import time
import logging
import requests
import asyncio
import pyppdf.patch_pyppeteer
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


#logging.basicConfig(level = logging.ERROR)
BASE_URL = "https://sports.bwin.es"

class BWIN_Scrapper(threading.Thread):

    def __init__(self, match, time_to_sleep = 60):
        threading.Thread.__init__(self)
        self.match = match
        self.time_to_sleep = time_to_sleep
        self._running = True
        self.KEY_WORDS = ["médico", "médica", "medico", "medica", "mto", "(mto)", "medical", "pausa", "timeout", "retired"]


    def run(self):
        prev_comments = []

        #CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
        CHROMEDRIVER_PATH = './chromedriver'
        WINDOW_SIZE = "1920,1080"

        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        #chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)


        while (self._running):
            try:
                driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
                #driver.implicitly_wait(20)
                driver.get(BASE_URL + self.match)
                element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "scoreboard-message")))
                #time.sleep(25)
                # Abrimos panel de comentarios
                #driver.find_element_by_class_name("scoreboard-message").click()
                element.click()

                # Obtenemos la lista donde estan los comentarios
                comment_events = driver.find_element_by_class_name("scoreboard-message-list")
                #logging.info("ENCONTRAMOS COMENTARIOS")

                info = driver.find_element_by_class_name("header-content")
                infosoup = BeautifulSoup(info.get_attribute('innerHTML'), features='html.parser')

                # Creamos el objeto Soup con el HTML de la lista de comentarios
                soup = BeautifulSoup(comment_events.get_attribute('innerHTML'), features='html.parser')
                driver.close()

                p = infosoup.findAll("div", {"class": "participant-name-value"})
                participants = []
                for participant in p:
                    participants.append(participant.text)

                #print("PARTICIPANTS: ")
                #print(participants)

                # Encontramos cada comentario en la lista de comentarios
                messages = soup.findAll("ms-scoreboard-message", {"class":"scoreboard-message"})

                commentaries = []
                # Obtenemos el texto de cada comentario en la lista
                for message in messages:
                    toAppend = message.find("span", {"class":"time"}).text # la hora
                    toAppend = toAppend + " " + message.find("span", {"class":"text"}).text # el comentario
                    commentaries.append(toAppend)

                # Encontramos cuales son los nuevos comentarios respecto a la anterior busqueda
                new_comments = list(set(commentaries) - set(prev_comments))
                for phrase in new_comments:
                    found = False
                    for key_word in self.KEY_WORDS:
                        if (found is True):
                            break
                        for word in phrase.split():
                            if (key_word == word.lower()):
                                print("\n\n\n\n\n\n")
                                print(phrase.upper())
                                print("\n\n\n\n\n\n")
                                if (phrase.split()[-1].lower() == "unknown"):
                                    phrase += " in " + participants[0] + " vs " + participants[1]
                                    print("PHRASE: " + phrase)

                                with open("discord_comments.txt", "a") as myfile:
                                    myfile.write(phrase + "\n")
                                with open("telegram_comments.txt", "a") as myfile:
                                    myfile.write(phrase + "\n")

                                found = True
                                break


                print(new_comments)
                prev_comments = commentaries
                time.sleep(self.time_to_sleep)

            except Exception as e:
                #driver.close()
                logging.error("Error en el partido {} de BWIN scrapper {}".format(self.match, e))
                time.sleep(self.time_to_sleep)
        exit(0)


    def terminate(self):
        self._running = False
