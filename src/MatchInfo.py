#!/usr/bin/env

class MatchInfo:

    def __init__(self, id, url):
        self.id = id
        self.url = url

    def get_id(self):
        return self.id

    def get_url(self):
        return self.url
