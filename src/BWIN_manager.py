#!/usr/bin/env

import threading
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from BWIN_scrapper import BWIN_Scrapper

#logging.basicConfig(level = logging.ERROR)

class BWIN_Manager(threading.Thread):

    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url
        self.BWIN_threads = {}

    def run(self):
        self.create_threads()

    def create_threads(self):
        prev_matches = []

        while True:
            matches_urls = self.search_matches()

            if (matches_urls is None):
                time.sleep(30)
                continue

            # KEY: MATCH_URL  VALUE:THREAD
            #logging.info('Creating BWIN scraper threads...')
            logging.info('Hay {} partidos en vivo ahora mismo {}'.format(len(matches_urls), matches_urls))

            # Check of the matches that have been removed from live matches
            removed_matches = list(set(prev_matches) - set(matches_urls))
            logging.info('Lista de threads a terminar {}'.format(removed_matches))
            for removed_match in removed_matches:
                self.BWIN_threads[removed_match].terminate()
                self.BWIN_threads[removed_match].join()
                del self.BWIN_threads[removed_match]

            # Check of new matches available in live matches
            new_matches = list(set(matches_urls) - set(prev_matches))
            logging.info('La lista de nuevos partidos es: {}'.format(new_matches))
            for new_match in new_matches:
                thread = BWIN_Scrapper(new_match)
                logging.info('KEY {} VALUE {}'.format(new_match, thread))
                self.BWIN_threads[new_match] = thread
                thread.start()
                time.sleep(30)

            prev_matches = matches_urls

            #logging.info('El dict de threads es: {}'.format(self.BWIN_threads))


            # TIME ELAPSED BETWEEN EACH CHECK OF THE LIVE MATCHES
            time.sleep(500)


    def search_matches(self):
        #CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
        CHROMEDRIVER_PATH = './chromedriver'
        WINDOW_SIZE = "1920,1080"

        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

        try:
            driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                      chrome_options=chrome_options)

            print("ANTES DE ENTRAR EN LA PAGINA")
            driver.implicitly_wait(20)
            driver.get(self.url)
            time.sleep(15)
            print("DESPUES DEL SLEEP")
            main_component = driver.find_element_by_class_name("app-root")
            soup = BeautifulSoup(main_component.get_attribute('innerHTML'), features='html.parser')
            driver.close()

            events = soup.find("div", {"class":"grid-wrapper"}).findAll("ms-event", {"class":"grid-event ms-active-highlight"})

            matches = []
            for match in events:
                matches.append(match.find("a")['href'])

            #print(matches)
            return matches

        except Exception as e:
            #logging.error("Exception in search_matches {}".format(e))
            logging.error("No se han encontrado partidos, error: {}".format(e))
            return None
