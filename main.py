from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

# Функция, которая обрабатывает команду /start
def start(update: Update, context: CallbackContext) -> None:
    # Создаем клавиатуру с кнопкой
    keyboard = [
        [InlineKeyboardButton("Пройти тест", url='https://forms.yandex.ru/u/67d8756002848f4bec767854/')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с кнопкой
    update.message.reply_text(
        "Спасибо, я уже ищу 👀 решение!\n\n"
        "А пока предлагаю тебе пройти короткий онлайн-тест, который поможет узнать ещё немного о тебе 🫵🏼",
        reply_markup=reply_markup
    )

def main() -> None:
    # Создаем экземпляр Updater и передаем ему токен вашего бота
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрация обработчика команды /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Запуск бота
    updater.start_polling()

    # Ожидание завершения работы бота
    updater.idle()

if __name__ == '__main__':
    main()
