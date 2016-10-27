import botogram
import sqlite3
import time
from config import *
from database import *

#get last record
def actual_position(store):
    c.execute("SELECT posizione FROM %s ORDER BY id DESC LIMIT 1" % (store,))
    posizione=c.fetchone()[0]
    return (posizione)

#get the stats (MAX, MIN, AVG) of the records
def the_3_stats(x, store):
    c.execute("SELECT %s(posizione) FROM %s" % (x, store,))
    result=c.fetchone()[0]
    result=round(result,2)
    return (result)


#get the hystory of records
#users can choose how many of them they want to receive
#they are sorted in order to get only the latest
def hystory(chat, message, args, store):
    if chat.type!="private":
        message.reply("Questo comando è utilizzabile solo in chat privata.")
    else:
        if len(args)!=1:
            message.reply("dopo il comando scrivi quanti post indietro vuoi vedere. Es: /storicoappstore 10 per \
vedere le ultime dieci posizioni.")
        else:
            try:
                numero=int(args[0])
                if numero<1:
                    message.reply("usa solo numeri maggiori di 0")
                else:
                    c.execute("SELECT posizione,OrderDate FROM %s ORDER BY OrderDate DESC LIMIT (?)" % (store,), (numero,))
                    hystory=c.fetchall()
                    messaggio="STORICO "+str(store)+":\n\n"
                    for line in hystory:
                        messaggio+=(" "+str(line[0])+"      ("+str(line[1])+")\n___________________\n")
                    n=4000
                    for i in range(0, len(messaggio), n):
                        s=[messaggio[i:i+n]]
                        message.reply(s, syntax="plain")
                        time.sleep(0.5)
            except ValueError:
                message.reply("usa numeri")



#stats about how many users the bot has. (total and notifications on - users)
def stats_all():
    c.execute("SELECT COUNT(id) FROM chat")
    totale=c.fetchone()[0]
    c.execute("SELECT COUNT(id) FROM chat WHERE iscritto=(?)",(1,))
    totale_attive=c.fetchone()[0]
    return (str(totale), str(totale_attive))

#stats for types (total and notifications on - users)
def stats_type(tipo):
    c.execute("SELECT COUNT(id) FROM chat WHERE tipo=(?)",(tipo,))
    anyone=c.fetchone()[0]
    c.execute("SELECT COUNT(id) FROM chat WHERE tipo=(?) AND iscritto=(?)",(tipo,1))
    notif_on=c.fetchone()[0]
    return (str(anyone), str(notif_on))


#create a message with users' bot stats
def stats_message():
    message="Totali: "+stats_all()[0]+" notified: "+stats_all()[1]+"\n"
    lista=["private", "group", "supergroup"]
    for i in lista:
        message+=i+": "+stats_type(i)[0]+" notified: "+stats_type(i)[1]+"\n"
    return (message)



#enable and disable notifications
def notif(chat, message, args, valore):
    """
    Riattiva i messaggi per le variazioni di posizioni
    """
    if chat.type!="private" and message.sender not in chat.admins:
        message.reply("Questo comando può darlo solo un admin.")
    else:
        id_chat=int(chat.id)
        c.execute("UPDATE chat SET iscritto=(?) WHERE id=(?)",(valore, id_chat))
        conn.commit()

#send broadcast to any user
def broadcast(chat, message, bot):
    testo=message.text
    testo=testo.replace("broadcast->", "")
    c.execute("SELECT id FROM chat")
    lista_chat=(c.fetchall())
    final_list=[]
    for chat_singola in lista_chat:
        final_list.append(chat_singola[0])
    bot.chat(owner).send("inizio invio")
    for chat in final_list:
        try:
            bot.chat(chat).send(testo)
        except botogram.ChatUnavailableError:
            c.execute("DELETE FROM chat WHERE id=?",(chat,))
            conn.commit()
        except botogram.APIError:
            c.execute("DELETE FROM chat WHERE id=?",(chat,))
            conn.commit()
        time.sleep(0.4)
    bot.chat(owner).send("ho inviato a tutti:\n\n"+testo)


