import requests
import configparser
import csv
import re

class Game:
    title = "SQL Island Escape Room"
    sheet_csv_url : str

    def __init__(self, game_data_store):
        self.game_data_store = game_data_store
        config = configparser.ConfigParser()
        config.read("config.ini")
        

    def check_firstmessage(self):
        return False

    def check_er(self):
        return False

    def check_connected(self):
        return False

    def check_create_table(self):
        return False

    def check_foreign_key(self):
        return False

    def check_inhabitants(self):
        return False

    def check_chief(self):
        return False

    def check_select_count(self):
        return False