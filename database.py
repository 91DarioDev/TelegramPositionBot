import botogram
import sqlite3
from config import *

#create the db and open it
conn = sqlite3.connect(db_name)
c = conn.cursor()
#table containing users. subscribed by default.
try:
    c.execute("CREATE TABLE chat(id INTEGER PRIMARY KEY, iscritto INTEGER NOT NULL DEFAULT (1), tipo TEXT)")
except:
    pass
#table containing posistion and date 
try:
    c.execute("CREATE TABLE PlayStore(id INTEGER PRIMARY KEY, posizione INTEGER, OrderDate datetime NOT NULL DEFAULT(datetime()))")
except:
    pass
#table containing posistion and date 
try:
    c.execute("CREATE TABLE appstore(id INTEGER PRIMARY KEY, posizione INTEGER, OrderDate datetime NOT NULL DEFAULT(datetime()))")
except:
    pass
conn.commit()

#automatically add to the database users chatting with the bot. subscribed by default -> default is 1
def add_chats_to_db(chat, message):
    id_chat=int(chat.id)
    tipo=str(chat.type)
    try:
        c.execute("INSERT INTO chat(id, tipo) VALUES(?,?)",(id_chat, tipo))
    except sqlite3.IntegrityError:
        pass
        #the user id is already in the DB
    conn.commit()

#backup the whole db
def backup_database(chat, message, args):
    chat.send_file(db_name)
