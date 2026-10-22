import requests
import sys
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
  for entry in result:
    (table,column,cname,ref_table,ref_column) = entry
    schema[table][column]["fk"] = {"table":ref_table, "column":ref_column }

  for table in want:
    # Check if table exists
    if not table in schema:
      print("Table missing: "+table)
      return False   # Table does not exist
    for column in want[table]:
      data = want[table][column]

      # Check if column exists
      if not column in schema[table]:
        print("Column missing in table "+table+": "+column)
        return False   # Column does not exist

      # Checking primary key attributes
      key = False if "key" not in schema[table][column] else schema[table][column]["key"]
      if (not "key" in data and key or "key" in data and data["key"] != key) and key != "MUL": 
        print("Key error "+table+"/"+column+": "+(key or "(None)")+" != "+("(None)" if not "key" in data else data["key"]))
        return False   # Key wrong

      # Checking data types
      stype = schema[table][column]["type"]
      wtype = data["type"] if type in data else False
      if wtype and wtype == "text" and "text" not in stype and "varchar" not in stype:
        print("Text type error "+table+"/"+column+": "+stype+" != "+wtype)
        return False   # Type wrong
      if wtype and wtype == "int" and "int" not in stype:
        print("Int type error "+table+"/"+column+": "+stype+" != "+wtype)
        return False   # Type wrong

      # Checking foreign keys
      fk = False if not "fk" in schema[table][column] else schema[table][column]["fk"]
      if "fk" in data and not fk:
        print("FK missing for "+table+"/"+column)
        return False   # Foreign key wrong
      if "fk" in data and fk and (fk["table"] != data["fk"]["table"] or fk["column"] != data["fk"]["column"]):
        print("FK wrong for "+table+"/"+column+" (references "+fk["table"]+"/"+fk["column"]+")")
        return False   # Foreign key wrong
      elif ("fk" not in data and fk):
        print("Unexpected FK in "+table+"/"+column)
        return False   # Foreign key wrong

  return True

def check_table_contents (csvfile, sqlquery):
    try:
      contents_db = query(sqlquery)
      contents_file = open(csvfile)
      contents_csv = csv.reader(contents_file, delimiter=',', quotechar='\'')
      for row in contents_db:
        csvrow = tuple(next(contents_csv,[]))
        dbrow = tuple(map(str,row))
        if csvrow != dbrow:
          print("Mismatch: db:"+str(dbrow)+", expected: "+str(csvrow))
          return False
    except Exception as e:
      raise e
      print(f'Error checking contents: {e}')
      return False
    csvrow = tuple(next(contents_csv,[]))
    if csvrow != ():
      print("Too few rows in db")
      return False

    return True

def last_query(username, contains='None'):
  result = query(f"SELECT argument FROM mysql.general_log WHERE command_type='Query' AND user_host LIKE '{username}[%' AND event_time > date_sub(now(), interval 10 second) order by event_time desc");

  for item in result:
     q = item[0].decode("utf-8")
     if (contains.lower() in q.lower()):
       return q

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
       return check_table_contents("assets/inhabitants.csv", "SELECT personid,name,job,gender,gold,home FROM inhabitants ORDER BY personid")

    def check_chief(self):
      result = query("select count(*) from villages where chief = (select personid from inhabitants where name = 'Helen Grasshead');");
      count = result[0][0]
      return count == 3

    def check_select_count(self):
      q = last_query("cscape_sql_island", "group")
      if not q:
        return False
      print("Checking query: "+q)
      result = query(q)
      r = {}
      for item in result:
        r[item[0]] = item[1]

      if "Monkeycity" in r:
        if r["Monkeycity"] == 6 and r["Cucumbertown"] == 5 and r["Onionville"] == 8:
           return True
      elif 1 in r and 2 in r and 3 in r:
        if r[1] == 6 and r[2] == 5 and r[3] == 8:
           return True
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

