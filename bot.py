import botogram
import json
import time
import sqlite3
import urllib.request
from database import *
from extrafeatures import *
from config import *

bot = botogram.create(token)
bot.owner = your_name
bot.about = description


#start checking positions
def boot(bot):
    check(playstore_parse(), "PlayStore")
    check(appstore_parse(), "appstore")

#check if an error occurred (the html of the pages changed),
#telegram is not in the leaderboard etc or send notifications
def check(x, store):
    if x==False:
        #send the message to the owner an error occured
        bot.chat(owner).send("an error occurred on "+str(store))
    else:
        posizione=x
        cfr_p=cfr(store)
        if cfr_p!=posizione:
            final(posizione, store)

#check the position on appstore
def playstore_parse():
    link = "https://play.google.com/store/apps/collection/topselling_free?gl=it"
    request = urllib.request.urlopen(link)
    page = request.read()
    page=page.decode(encoding='UTF-8')
    stringa="href=\"/store/apps/details?id=org.telegram.messenger\" aria-label="
    if stringa in page:
        posizione=page[page.find(stringa):].split()[2]
        if posizione.endswith("."):
            while "." in posizione:
                posizione=posizione.replace(".","")
            posizione=int(posizione)
            return (posizione)
        #send and advice to the owner if the string doesn't end with the dot. something changed
        else:
            return False
    #send an advice to the owner if the string isn't in the file.
    else:
        return False

#check the position on appstore
def appstore_parse():
    link = "http://www.apple.com/it/itunes/charts/free-apps/"
    request = urllib.request.urlopen(link)
    page = request.read()
    stringa="Telegram Messenger"
    if stringa in str(page):
        posizione=str(page)[:str(page).find(stringa)].split("</strong>")[-2]
        posizione=posizione[str(posizione).find("<strong>")+8:]
        if posizione.endswith("."):
            while "." in posizione:
                posizione=posizione.replace(".","")
            posizione=int(posizione)
            return (posizione)
        #send and advice to the owner if the string doesn't end with the dot. something changed
        else:
            return False
    #send an advice to the owner if the string isn't in the file.
    else:
        return False

#check last records to compare
def cfr(x):
    c.execute("SELECT posizione FROM %s ORDER BY id DESC LIMIT 1" % (x,))
    cfr=c.fetchone()[0]
    return (cfr)

#get a list of notification subscribed users
def subscribed():
    c.execute("SELECT id FROM chat WHERE iscritto=1")
    lista_chat=(c.fetchall())
    return (lista_chat)

#save new records in DB and send the notification to anyone (subscribed)
def final(posizione, store):
    lista_chat=subscribed()
    cfr2=cfr(store)

    if store=="appstore":
        emoji="\U0001F34E"
    if store=="PlayStore":
        emoji="\U0001F916"

    variazione=""
    somma=(int(cfr2)-int(posizione))
    if somma<0:
        variazione+=str(somma)+ "\U0001f53d"
        start="<i>"
        end="</i>"
    if somma>0:
        variazione+="+"+str(somma)+ "\U0001f53c"
        start="<b>"
        end="</b>"

    c.execute("INSERT INTO %s(posizione) VALUES(?)" % (store,),(posizione,))
    conn.commit()
    for chat_singola in lista_chat:
        chat_singola=(chat_singola)[0]
        try:
            bot.chat(chat_singola).send(emoji+start+"-"+str(store)+": "+str(posizione)+"\n  "+variazione+end, syntax="html")
        #delete from the DB chats no more active
        except botogram.ChatUnavailableError:
            c.execute("DELETE FROM chat WHERE id=?",(chat_singola,))
            conn.commit()
        except botogram.APIError:
            c.execute("DELETE FROM chat WHERE id=?",(chat_singola,))
            conn.commit()
        time.sleep(0.4)


#start the check every x seconds
@bot.timer(1800)
def start(bot):
    boot(bot)

#add users texting with the bot to the DB
@bot.before_processing
def add_chats_to_db2(chat, message):
    add_chats_to_db(chat, message)

#get a backup of the DB
@bot.command("database", hidden=True)
def backup_database2(chat, message, args):
    if message.sender.id==owner:
        backup_database(chat, message, args)

#send last records
@bot.command("posizioniattuali")
def posizioni_attuali(chat, message, args):
    """
    Posizioni attuali
    """
    chat.send("<b>PlayStore:</b> "+str(actual_position("PlayStore"))+"\n<b>appstore:</b> "+str(actual_position("appstore")), syntax="html")

#send the average of the positions
@bot.command("media")
def medium(chat, message, args):
    """
    mostra la media tra tutte le posizioni loggate
    """
    chat.send("<b>PlayStore:</b> "+str(the_3_stats("AVG","PlayStore"))+"\n<b>appstore:</b> "+str(the_3_stats("AVG","appstore")), syntax="html")

#send the best position
@bot.command("migliore")
def maximum(chat, message, args):
    """
    mostra la posizione migliore mai raggiunta 
    """
    chat.send("<b>PlayStore:</b> "+str(the_3_stats("MIN","PlayStore"))+"\n<b>appstore:</b> "+str(the_3_stats("MIN","appstore")), syntax="html")

#send the lower position
@bot.command("peggiore")
def minimum(chat, message, args):
    """
    mostra la posizione peggiore mai raggiunta
    """
    chat.send("<b>PlayStore:</b> "+(str(the_3_stats("MAX","PlayStore")))+"\n<b>appstore:</b> "+(str(the_3_stats("MAX","appstore"))), syntax="html")

#send the hystory of logs
@bot.command("logsappstore")
def storico_appstore(chat, message, args):
    """
    mostra uno storico delle posizioni su appstore
    """
    hystory(chat, message, args, "appstore")

#send the hystory of logs
@bot.command("logsplaystore")
def storico_playstore(chat, message, args):
    """
    mostra uno storico delle posizioni su PlayStore
    """
    hystory(chat, message, args, "PlayStore")

#get a stat of chats using the bot
@bot.command("chat", hidden=True)
def numero_chat(chat, message, args):
    if message.sender.id==owner:
        chat.send(stats_message())

#enable notifications
@bot.command("getnotification")
def yes_notif(chat, message, args):
    """
    Riattiva i messaggi per le variazioni di posizioni
    """
    notif(chat, message, args, 1)
    #a message you have been subscribed to notifications
    message.reply("<b>Iscritto!</b> Ora riceverai messaggi per le variazioni di posizioni. Se non vuoi: /stopupdate.", syntax="html")

#disable notifications
@bot.command("stopnotification")
def no_notif(chat, message, args):
    """
    Riattiva i messaggi per le variazioni di posizioni
    """
    notif(chat, message, args, 0)
    #a message you disabled notifications
    message.reply("<b>Disiscritto!</b> Potrai continuare a usare il bot senza doverlo bloccare, non ricevendo più le \
notifiche. Se ci ripensi /getupdate", syntax="html")

#send a broadcast to every user
@bot.process_message
def broadcast2(chat, message, bot):
    if message.text:
        if message.sender.id==owner and message.text.startswith("broadcast->"):
            broadcast(chat, message, bot)

#get a preview of the broadcast you would like to send
@bot.process_message
def preview(chat, message):
    if message.text:
        if message.sender.id==owner and message.text.startswith("preview->"):
            testo=message.text
            testo=testo.replace("preview->","")
            message.reply(testo)

#get info from an ID
@bot.command("infoid", hidden=True)
def infobyid(chat, message, args):
    if message.sender.id==owner:
        if len(args)==1:
            us=args[0]
            try:
                trid=bot.api.call("getChat", {"chat_id":us})
                dizionario=(trid["result"])
                messaggio=""
                dizionario_lista=list(dizionario.keys())
                for i in dizionario_lista:
                    if i == "username":
                        dizionario[i]="@"+dizionario[i]
                    messaggio+= (str(i)+": "+str(dizionario[i])+"\n")
                message.reply(messaggio, syntax="plain")
            except botogram.ChatUnavailableError as e:
                message.reply(e.reason)
            except (botogram.APIError) as e:
                message.reply(e.description)

#this command should be run the first time you run the bot.
#in this way the DB won't be empty but it will add suddenly the right positions of the moment.
def first_time_in(store, posizione):
    c.execute("INSERT INTO %s(posizione) VALUES(?)" % (store,),(posizione,))
    conn.commit()

#only in case of new/empty db such as for the first time.
@bot.command("firstime", hidden=True)
def first_time(chat, message, args):
    if message.sender.id==owner:
        if (playstore_parse()) is not False:
            first_time_in("PlayStore", playstore_parse())
            message.reply("ok. PlayStore is fine. You can start using the bot")
        else:
            message.reply("PlayStore: an error occurred. please check the parse function.")
        if (appstore_parse()) is not False:
            first_time_in("appstore", appstore_parse())
            message.reply("ok. Appstore is fine. You can start using the bot")
        else:
            message.reply("Appstore: an error occurred. please check the parse function.")


bot.process_backlog=True
if __name__ == "__main__":
    bot.run()
