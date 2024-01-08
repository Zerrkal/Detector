from telegram import Bot, Update
from telegram.error import TelegramError
from telegram.ext import Updater, CommandHandler, CallbackContext

class AlertNotificationTelegram:
    def __init__(self):
        token = '6659513814:AAHmExNMl75UQ7DgqAlGY5W-QGG07uRTiMQ'  # Ваш токен бота
        self.bot = Bot(token)
        self.updater = Updater(token)  # Видалено use_context=True
        self.chat_id = None
        self.notifications_enabled = False
        self.activate_chat()

    def set_chat_id(self, chat_id):
        self.chat_id = chat_id

    def get_chat_id(self):
        return self.chat_id
    
    def start(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        self.chat_id = chat_id  # Змінено на self.chat_id

        update.message.reply_text(f"Чат активовано! Ваш chat_id: {chat_id}")
        # self.send_message('Привіт! Це тестове повідомлення.')

    def enable_notifications(self, update: Update, context: CallbackContext):
        self.notifications_enabled = True
        update.message.reply_text(f"Сповіщення включено. Ваш chat_id: {self.chat_id}")

    def disable_notifications(self, update: Update, context: CallbackContext):
        self.notifications_enabled = False
        update.message.reply_text("Сповіщення вимкнено.")

    def activate_chat(self):
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('enable', self.enable_notifications))
        dispatcher.add_handler(CommandHandler('disable', self.disable_notifications))
        self.updater.start_polling()

    def send_message(self, message):
        if self.chat_id:
            try:
                self.bot.send_message(self.chat_id, message)
            except TelegramError as e:
                print(f"Error: {e}")
        else:
            print("Chat ID не встановлено.")

    def send_image(self, photo = None, caption=None):
        if photo is not None:
            try:
                # photo.seek(0)  # Перемотати на початок файлу
                self.bot.send_photo(self.chat_id, photo=photo, caption=caption)
            except TelegramError as e:
                print(f"Помилка при відправленні фото: {e}")
        elif caption is not None:
            self.send_message(caption)

# # Використання класу бота
# my_bot = AlertNotificationTelegram()

# # Активація прийому повідомлень
# my_bot.activate_chat()

# # Приклад відправлення повідомлення
# my_bot.send_message('Привіт! Це тестове повідомлення.')

# current_chat_id = my_bot.get_chat_id()
# print(f"Поточний chat_id: {current_chat_id}")