# SQL Island Escape Room

SQL Island is an educational escape room game for the CSCape framework that teaches database concepts through an interactive storytelling experience.

![SQL Island Characters](sql_island_bg.jpg)

## Setup

* Deploy phone folder to web server
* Create database and user
* Set permissions 777 on phone/chat.txt
* Create config.ini with database credentials


## Configuration

Create a `config.ini` file in the main directory or ensure the following configuration exists:

```ini
[general]
check_interval_seconds = 5
game_module = cscape_sql_island

[cscape_sql_island]
chat_server_url = https://escape.othdb.de
db_host = 
db_user =
db_password = 
```

**File Permissions:**

Ensure the chat file is writable by the web server:
```bash
chmod 777 phone/chat.txt
```

## Game Levels

The escape room contains the following challenges:

1. **check_firstmessage** - Send a message to Arthur via chat
2. **check_er** - Team name is sent and Arthur confirms your ER diagram is correct
3. **check_connected** - Connect to the database server using credentials found in the room
4. **check_create_table** - Create the inhabitants table based on the ER diagram
5. **check_foreign_key** - Add a foreign key constraint from the chief column in the village table to the inhabitants table using ALTER TABLE
6. **check_inhabitants** - Import the inhabitants data from a backup file (located in a suitcase in the room)
7. **check_chief** - Restore the chief values that were set to NULL by the DELETE operation with an UPDATE command
8. **check_select_count** - Write a SQL query to count inhabitants per village to complete the escape