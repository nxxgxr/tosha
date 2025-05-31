import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import asyncio
from dotenv import load_dotenv
import telegram.error

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
SENT_GROUP_ID = os.getenv('SENT_GROUP_ID')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Проверка переменных окружения
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не задан в .env")
    raise ValueError("Необходимо задать BOT_TOKEN в файле .env")
if not SENT_GROUP_ID:
    logger.error("SENT_GROUP_ID не задан в .env")
    raise ValueError("Необходимо задать SENT_GROUP_ID в файле .env")

# Вывод SENT_GROUP_ID для отладки
logger.info(f"SENT_GROUP_ID: {SENT_GROUP_ID}")

# Удаление вебхука при старте
async def clear_webhook():
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.deleteWebhook()
        logger.info("Webhook успешно удален")
    except telegram.error.TelegramError as e:
        logger.error(f"Ошибка при удалении вебхука: {e}")

# Команда для получения Chat ID
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text(f"Chat ID: {chat_id}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open('hello.jpg', 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="Привет, друг! 👋🏼\n\n"
                "Меня зовут Тоша, рад приветствовать тебя!)\n\n"
                "Для начала опиши проблему, которая тебя волнует."
            )
    except FileNotFoundError:
        logger.error("Файл hello.jpg не найден")
        await update.message.reply_text("Привет, друг! 👋🏼\n\n"
                                       "Меня зовут Тоша, рад приветствовать тебя!)\n\n"
                                       "Для начала опиши проблему, которая тебя волнует.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user = update.message.from_user

    group_message = (
        "🚨 Новое сообщение от пользователя:\n\n"
        f"👤 Пользователь: @{user.username}\n"
        f"💬 Сообщение: {user_message}"
    )

    try:
        await context.bot.send_message(
            chat_id=SENT_GROUP_ID,
            text=group_message
        )
    except telegram.error.BadRequest as e:
        logger.error(f"Ошибка отправки сообщения в группу {SENT_GROUP_ID}: {e}")
        await update.message.reply_text(f"Произошла ошибка: {e}. Проверьте, добавлен ли бот в группу по ссылке https://t.me/+A_6CTS_w0QdjZTcy.")
        return

    await update.message.reply_text(
        "Спасибо, я уже ищу 👀 решение!\n\n"
        "А пока предлагаю тебе пройти короткий онлайн-тест, который поможет узнать ещё немного о тебе 🫵🏼",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Пройти тест и узнать свои сильные стороны!", url="https://docs.google.com/forms/d/e/1FAIpQLScZQidI6fqnU4uSWX9Hy41ghGf8hsS7PR2yxYK3_s957vA7Ew/viewform?usp=header")]
        ])
    )

    await asyncio.sleep(35)

    try:
        with open('like.jpg', 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="Спасибо за прохождение!⚡️\n\n"
                "Я выявил, что ты — отличный человек и у тебя есть большой потенциал для покорения любых вершин⛰️\n\n"
                "Скоро с тобой свяжется один из наших специалистов, чтобы дать тебе профессиональный план дальнейших действий.\n\n"
                "Пожалуйста, оцени мою работу, чтобы с каждым разом я становился лучше!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👍🏻", callback_data="like")],
                    [InlineKeyboardButton("👎🏼", callback_data="dislike")]
                ])
            )
    except FileNotFoundError:
        logger.error("Файл like.jpg не найден")
        await update.message.reply_text(
            "Спасибо за прохождение!⚡️\n\n"
            "Я выявил, что ты — отличный человек и у тебя есть большой потенциал для покорения любых вершин⛰️\n\n"
            "Скоро с тобой свяжется один из наших специалистов, чтобы дать тебе профессиональный план дальнейших действий.\n\n"
            "Пожалуйста, оцени мою работу, чтобы с каждым разом я становился лучше!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👍🏻", callback_data="like")],
                [InlineKeyboardButton("👎🏼", callback_data="dislike")]
            ])
        )

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_reply_markup(reply_markup=None)

    feedback_type = "лайк 👍🏻" if query.data == "like" else "дизлайк 👎🏼"

    feedback_message = (
        "📢 Человек @{} дал фидбэк: {}"
    ).format(query.from_user.username, feedback_type)

    try:
        await context.bot.send_message(
            chat_id=SENT_GROUP_ID,
            text=feedback_message
        )
    except telegram.error.BadRequest as e:
        logger.error(f"Ошибка отправки фидбэка в группу {SENT_GROUP_ID}: {e}")
        await query.message.reply_text(f"Произошла ошибка: {e}. Проверьте, добавлен ли бот в группу по ссылке https://t.me/+A_6CTS_w0QdjZTcy.")
        return

    await query.message.reply_text("Спасибо за ответ⚡️ До скорых встреч!")

def main():
    logger.info("🚀 Запуск бота...")
    logger.info(f"SENT_GROUP_ID: {SENT_GROUP_ID}")  # Отладка SENT_GROUP_ID
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getid", get_chat_id))  # Команда /getid
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_rating, pattern="^(like|dislike)$"))

    logger.info("🤖 Бот успешно запущен!")
    asyncio.run(clear_webhook())
    try:
        application.run_polling()
    except telegram.error.Conflict as e:
        logger.error(f"Конфликт getUpdates: {e}")
        logger.info("Попытка перезапустить polling через 10 секунд...")
        asyncio.sleep(10)
        application.run_polling()

if __name__ == '__main__':
    main()
