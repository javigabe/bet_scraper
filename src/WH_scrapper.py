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


BASE_URL = "https://sports.williamhill.es"

class WH_Scrapper(threading.Thread):

    def __init__(self, match, time_to_sleep = 20):
        threading.Thread.__init__(self)
        self.match = match
        self.time_to_sleep = time_to_sleep
        self._running = True
        self.KEY_WORDS = ["médico", "médica", "medico", "medica", "mto", "(mto)",
        "medical", "pausa", "timeout", "retired"]


    def run(self):
        while (self._running):
            request = requests.get(BASE_URL + self.match)
            if (request.status_code > 400):
                # PAGE MAY BE BROKEN
                exit(1)

            match_data = BeautifulSoup(request.text, 'html.parser')
            scoreboard = match_data.find("div", {"id": "scoreboard_frame"})
            #logging.info("scoreboard: {} y url: {}".format(scoreboard, self.match))

            if (scoreboard is not None):
                scoreboard_url = scoreboard["data-launch-url"]
                self.get_comments(scoreboard_url)
                break

            #print(scoreboard)
            time.sleep(self.time_to_sleep)
        return 0


    def terminate(self):
        self._running = False


    def get_comments(self, scoreboard):

        CHROMEDRIVER_PATH = './chromedriver' #'/usr/local/bin/chromedriver' #
        WINDOW_SIZE = "1920,1080"

        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

        prev_comments = []

        while (self._running):

            try:
                driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                          chrome_options=chrome_options)

                driver.get(scoreboard)
                time.sleep(5)
                driver.find_element(By.ID, "comments_bar").click() # Allows comments
                driver.implicitly_wait(2)
                commentaries = driver.find_element(By.ID, "list_commentaries").text.split("\n")
                driver.close()

                new_comments = list(set(commentaries) - set(prev_comments))
                found = False
                for phrase in new_comments:
                    if (found is True):
                        break
                    for key_word in self.KEY_WORDS:
                        for word in phrase.split():
                            if (key_word == word.lower()):
                                with open("comments.txt", "a") as myfile:
                                    myfile.write(phrase + "\n")
                                found = True
                                print(phrase)
                                break

                #print(new_comments)

                prev_comments = commentaries
                time.sleep(200)


            except Exception as e:
                #logging.error("Exception in get_comments {}".format(e))
                #logging.error("Fallo el partido {}".format(self.match))
                time.sleep(200)
