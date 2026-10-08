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
        config.read("/var/www/html/cscape/config.ini")
        
        self.chat_server_url = config.get('cscape_sql_island', 'chat_server_url', fallback='')
        
        try:
            start_url = f"{self.chat_server_url.rstrip('/')}/start.php"
            requests.get(start_url)
        except Exception as e:
            print(f"Error calling start.php: {e}")
        

    def check_firstmessage(self):
        try:
            chat_url = f"{self.chat_server_url.rstrip('/')}/chat.txt"
            response = requests.get(chat_url)
            if response.status_code == 200:
                return response.text.strip() != ""
        except Exception as e:
            print(f"Error reading chat.txt: {e}")
        return False

    def check_er(self):
        try:
            chat_url = f"{self.chat_server_url.rstrip('/')}/chat.txt"
            response = requests.get(chat_url)
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                team_name = None
                for line in reversed(lines):
                    stripped_line = line.strip()
                    if stripped_line and stripped_line != "#ER_SOLVED":
                        team_name = stripped_line
                        break
                if team_name:
                    self.game_data_store.set("TEAM_NAME", team_name)
                er_solved = "#ER_SOLVED" in response.text
                return er_solved
        except Exception as e:
            print(f"Error reading chat.txt: {e}")
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