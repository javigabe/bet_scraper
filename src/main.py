#!/usr/bin/env


#import threading
import logging
import time
import requests
from bs4 import BeautifulSoup
from WH_scrapper import WH_Scrapper
from MatchInfo import MatchInfo
import pyppdf.patch_pyppeteer


URL = "https://sports.williamhill.es/betting/es-es/tenis"
BASE_URL = "https://sports.williamhill.es"
logging.getLogger().setLevel(logging.INFO)


class Launcher:


    def __init__(self, threads):
        # KEY: URL   VALUE: THREAD
        self.threads = threads
        self.launch_script()

    def get_matches(self):
        _weird_char = u"\xc3\xa2\xc2\x82\xc2\x8b"
        _replace = u"₋"
        events = []

        r = requests.get(URL)
        data = BeautifulSoup(r.text, features='html.parser')
        try:
            events = data.find("section", {"id":"in-play-now"}).findAll("div", {"class":"event"})
        except AttributeError as e:
            # No live matches at this moment
            logging.error("Exception in get_matches {}".format(e))


        return self._get_matches_info(events)


    def _get_matches_info(self, events):
        matches_urls = []

        for event in events:
            match_url = event.find("ul", {"class":"btmarket__content-margin"}).li.a['href']
            #match_id = event.find("ul", {"class":"btmarket__content-margin"}).\
                  #find("div", {"class":"btmarket__link-name btmarket__link-name--ellipsis show-for-desktop-medium"})

            #match = MatchInfo(match_id, match_url)
            #matches_info[match] = None
            matches_urls.append(match_url)


        return matches_urls

    def launch_script(self):
        prev_matches = []
        while True:
            matches_urls = self.get_matches()


            # KEY: MATCH_URL  VALUE:THREAD
            logging.info('Creating William Hill scraper threads...')
            logging.info('Hay {} partidos en vivo ahora mismo {}'.format(len(matches_urls), matches_urls))

            # Check of the matches that have been removed from live matches
            removed_matches = list(set(prev_matches) - set(matches_urls))
            logging.info('Lista de threads a terminar {}'.format(removed_matches))
            for removed_match in removed_matches:
                self.threads[removed_match].terminate()
                self.threads[removed_match].join()
                del self.threads[removed_match]

            # Check of new matches available in live matches
            new_matches = list(set(matches_urls) - set(prev_matches))
            logging.info('La lista de nuevos partidos es: {}'.format(new_matches))
            for new_match in new_matches:
                thread = WH_Scrapper(new_match)
                logging.info('KEY {} VALUE {}'.format(new_match, thread))
                self.threads[new_match] = thread
                thread.start()
                time.sleep(20)

            prev_matches = matches_urls

            logging.info('El dict de threads es: {}'.format(self.threads))


            # TIME ELAPSED BETWEEN EACH CHECK OF THE LIVE MATCHES
            time.sleep(500)


if __name__ == '__main__':
    Launcher({})
