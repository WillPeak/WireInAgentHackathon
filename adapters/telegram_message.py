import telebot

def send_message(token, chat_id, text):
    bot = telebot.TeleBot(token)
    bot.send_message(chat_id, text)


