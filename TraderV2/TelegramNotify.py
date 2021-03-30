import json
import telegram

def notify_ending(message):
    
    token = "1664179275:AAHSNRalCCJmfHrnpm0GnijgUbbH38u41vw"
    chat_id = "-514290409"

    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=message)

notify_ending('Test Mesajı, Python selamlar')