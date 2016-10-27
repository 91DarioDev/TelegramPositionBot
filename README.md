# TelegramPositionBot

This Telegram Bot (https://core.telegram.org/bots) (https://telegram.me/PosizioniTelegramBot) permits to monitor the Telegram positions on App Store and Play Store leaderboards. 
It checks every 30 min if they changed or not, if so it sends a Telegram message to all the subscribed (with notifications enabled) users with the new position and a comparison.

The bot saves new records in a SQL DB and users can have many informations with commands, like the positions history. It sends broadcasts and it has stats for subscribed users.

You can use this bot to check Telegram positions for your country or also other app (you have to modify the parse functions in the bot.py file, it currently works with italian leaderboards).

Before of running this bot, check the config.py file and look at the "firstime" command in the bot.py file (it's mandatory to work).

This uses botogram framework, so to run it, install Python and botogram (https://github.com/pietroalbini/botogram).

Internal comments are written in english, even if the strings for the users are currently in italian.

This bot has a lot of useful commands and utilities for the administrators:
- You can easily do a backup of the database
- You can elaborate stats of the bot usage from users
- You can send broadcasts to users

Also, users are allowed to:
- Get the current positions, the medium position in the stores, the best one and the worst and see the entire history
- Get subscribed or not to the delayed updates (every 30 minutes, if the position in the stores is changed)

Please check and respect the license file!
