import requests
import time
import configparser
import csv
import re
import mysql.connector

config = configparser.ConfigParser()

def check_tables (want):
  result = query("select TABLE_NAME,COLUMN_NAME,COLUMN_TYPE,COLUMN_KEY from information_schema.columns where TABLE_SCHEMA=(SELECT DATABASE())")
  schema = {}
  for entry in result:
    (table,column,column_type,key) = entry
    if not table in schema:
      schema[table] = {}
    schema[table][column] = { "type": column_type, "key": key }

  result = query("SELECT TABLE_NAME,COLUMN_NAME,CONSTRAINT_NAME,REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA=(SELECT DATABASE())")
  print(result)
  for entry in result:
    (table,column,cname,ref_table,ref_column) = entry
    schema[table][column]["fk"] = {"table":ref_table, "column":ref_column }

  for table in want:
    for column in want[table]:
      data = want[table][column]
      if not table in schema:
        print("Table missing: "+table)
        return False   # Table does not exist
      if not column in schema[table]:
        print("Column missing in table "+table+": "+column)
        return False   # Column does not exist
      key = False if "key" not in schema[table][column] else schema[table][column]["key"]
      if (not "key" in data and key or "key" in data and data["key"] != key) and key != "MUL": 
        print("Key error "+table+"/"+column+": "+(key or "(None)")+" != "+("(None)" if not "key" in data else data["key"]))
        return False   # Key wrong
      ctype = schema[table][column]["type"]
      if data["type"] == "text" and "text" not in ctype and "varchar" not in ctype:
        print("Text type error "+table+"/"+column+": "+ctype+" != "+data["type"])
        return False   # Type wrong
      if data["type"] == "int" and "int" not in ctype:
        print("Int type error "+table+"/"+column+": "+ctype+" != "+data["type"])
        return False   # Type wrong
      fk = False if not "fk" in schema[table][column] else schema[table][column]["fk"]
      if "fk" in data and not fk:
        print(schema)
        print("FK missing for "+table+"/"+column)
        return False   # Foreign key wrong
      if "fk" in data and fk and (fk["table"] != data["fk"]["table"] or fk["column"] != data["fk"]["column"]):
        print("FK wrong for "+table+"/"+column+" (references "+fk["table"]+"/"+fk["column"]+")")
        return False   # Foreign key wrong
      elif ("fk" not in data and fk):
        print("Unexpected FK in "+table+"/"+column)
        return False   # Foreign key wrong

  return True


class Game:
    title = "SQL Island Escape Room"

    def __init__(self, game_data_store):
        self.game_data_store = game_data_store
        config.read("./config.ini")
        
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
                    self.game_data_store.store("TEAM_NAME", team_name)
                er_solved = "#ER_SOLVED" in response.text
                return er_solved
        except Exception as e:
            print(f"Error reading chat.txt: {e}")
        return False

    def check_connected(self):
      result = query("SHOW PROCESSLIST")
      if result:
        for entry in result:
          if entry[1] == 'cscape_sql_island' and entry[3] == 'cscape_sql_island' and entry[4] == 'Sleep':
            return True
      return False

    def check_create_table(self):
        want = {
          "villages": {
            "villageid": { "type": "int", "key": "PRI" },
            "name": { "type": "text" },
            "chief": { "type": "int" }
          },
          "inhabitants": {
            "personid": { "type": "int", "key": "PRI" },
            "name": { "type": "text" },
            "gender": { "type": "text" },
            "job": { "type": "text" },
            "gold": { "type": "int" },
            "home": { "type": "int", "fk": { "table":"villages", "column":"villageid" } }
          }
        }
        return check_tables(want)

    def check_foreign_key(self):
        want = {
          "villages": {
            "villageid": { "type": "int", "key": "PRI" },
            "name": { "type": "text" },
            "chief": { "type": "int", "fk": { "table":"inhabitants", "column":"personid" } }
          },
          "inhabitants": {
            "personid": { "type": "int", "key": "PRI" },
            "name": { "type": "text" },
            "gender": { "type": "text" },
            "job": { "type": "text" },
            "gold": { "type": "int" },
            "home": { "type": "int", "fk": { "table":"villages", "column":"villageid" } }
          }
        }
        return check_tables(want)

    def check_inhabitants(self):
        return False

    def check_chief(self):
        return False

    def check_select_count(self):
        return False


def query (query):
  host = config.get('cscape_sql_island', 'db_host', fallback='localhost')
  port = config.get('cscape_sql_island', 'db_port', fallback='3306')
  dbname = config.get('cscape_sql_island', 'db_name', fallback='cscape_sql_island')
  user = config.get('cscape_sql_island', 'db_user', fallback='cscape_sql_island')
  pw   = config.get('cscape_sql_island', 'db_password', fallback='')
  connection = mysql.connector.connect(host=host, port=port, database=dbname, user=user, password=pw);

  if not connection.is_connected():
    print("Failed to connect to MySQL")
    return False

  cursor = connection.cursor()
  try:
    cursor.execute(query)
  except:
    return False

  result = []
  for entry in cursor:
    result.append(entry)

  return result

if __name__ == "__main__":
  config.read("../config.ini")
  found = False
  want = {
    "villages": {
      "villageid": { "type": "int", "key": "PRI" },
      "name": { "type": "text" },
      "chief": { "type": "int", "fk": { "table":"inhabitants", "column":"personid" } }
    },
    "inhabitants": {
      "personid": { "type": "int", "key": "PRI" },
      "name": { "type": "text" },
      "gender": { "type": "text" },
      "job": { "type": "text" },
      "gold": { "type": "int" },
      "home": { "type": "int", "fk": { "table":"villages", "column":"villageid" } }
    }
  }
  while not check_tables(want):
    time.sleep(1)
  print("Create table found!")


















