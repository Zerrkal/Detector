from telegram import Bot, Update
from telegram.error import TelegramError
from telegram.ext import Updater, CommandHandler, CallbackContext

from app_settings_conf import DetectionAppSetConfig


class AlertNotificationTelegram:
    def __init__(self, token):
        self.bot = Bot(token)
        self.updater = Updater(token)  # Видалено use_context=True
        self.set_chat_id()
        self.activate_chat()

    def set_chat_id(self):
        self.chat_ids = {}
        # Отримуємо ключі та значення як строки
        for chat_id_str, status_str in DetectionAppSetConfig.get_chat_ids().items():
            # Перетворення ключа у int і значення у булеве
            self.chat_ids[int(chat_id_str)] = True if status_str.lower() == 'true' else False

    
    def write_chat_id_to_config(self, chat_id, chat_id_status):
        # Перетворення булевого значення у строку
        status_str = 'true' if chat_id_status else 'false'
        DetectionAppSetConfig.set_chat_id(chat_id, status_str)
    
    def start(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        self.chat_ids[chat_id] = True
        self.write_chat_id_to_config(chat_id, self.chat_ids[chat_id])
        update.message.reply_text(f"Чат активовано! Ваш chat_id: {chat_id}")

    def enable_notifications(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        if chat_id in self.chat_ids:
            self.chat_ids[chat_id] = True
            self.write_chat_id_to_config(chat_id, self.chat_ids[chat_id])
            update.message.reply_text("Сповіщення увімкнено успішно.")

    def disable_notifications(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        if chat_id in self.chat_ids:
            self.chat_ids[chat_id] = False
            self.write_chat_id_to_config(chat_id, self.chat_ids[chat_id])
            update.message.reply_text("Сповіщення вимкнено успішно.")

    def activate_chat(self):
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('enable', self.enable_notifications))
        dispatcher.add_handler(CommandHandler('disable', self.disable_notifications))
        self.updater.start_polling()

    def send_message(self, message):
        self.set_chat_id()
        if self.chat_ids:
            for chat_id, chat_id_status in self.chat_ids.items():
                if chat_id_status:  # Перевірка, чи значення є True
                    try:
                        self.bot.send_message(chat_id, message)
                    except TelegramError as e:
                        print(f"Error sending message to {chat_id}: {e}")
        else:
            print("Chat ID не встановлено.")

    def send_image(self, photo = None, caption=None):
        self.set_chat_id()
        if photo is not None:
            for chat_id, chat_id_status in self.chat_ids.items():
                if chat_id_status:  # Перевірка, чи значення є True
                    try:
                        self.bot.send_photo(chat_id, photo=photo, caption=caption)
                    except TelegramError as e:
                        print(f"Error sending message to {chat_id}: {e}")