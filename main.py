import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import asyncio
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
SENT_GROUP_ID = os.getenv('SENT_GROUP_ID')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Команда /start получена")
    if not os.path.exists('hello.jpg'):
        logger.error("Файл hello.jpg не найден")
        await update.message.reply_text("Ошибка: изображение не найдено.")
        return
    with open('hello.jpg', 'rb') as photo:
        await update.message.reply_photo(
            photo=photo,
            caption="Привет, друг! 👋🏼\n\n"
            "Меня зовут Тоша, рад приветствовать тебя!)\n\n"
            "Для начала опиши проблему, которая тебя волнует."
        )

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    logger.info(f"Запрошен ID чата: {chat_id}")
    await update.message.reply_text(f"ID этого чата: {chat_id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Получено сообщение от @{update.message.from_user.username}: {update.message.text}")
    user_message = update.message.text
    user = update.message.from_user

    group_message = (
        "🚨 Новое сообщение от пользователя:\n\n"
        f"👤 Пользователь: @{user.username}\n"
        f"💬 Сообщение: {user_message}"
    )

    try:
        if not SENT_GROUP_ID or not SENT_GROUP_ID.startswith('-'):
            logger.error("SENT_GROUP_ID не задан или не является числовым ID группы")
            await update.message.reply_text("Ошибка: ID группы не настроен. Обратитесь к администратору.")
            return
        await context.bot.send_message(
            chat_id=SENT_GROUP_ID,
            text=group_message
        )
        logger.info("Сообщение отправлено в группу")
    except Exception as e:
        logger.error(f"Ошибка при отправке в группу: {e}")
        await update.message.reply_text("Произошла ошибка, попробуйте позже.")
        return

    await update.message.reply_text(
        "Спасибо, я уже ищу 👀 решение!\n\n"
        "А пока предлагаю тебе пройти короткий онлайн-тест, который поможет узнать ещё немного о тебе 🫵🏼",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Пройти тест и узнать свои сильные стороны!", url="https://forms.yandex.ru/u/67d8756002848f4bec767854/")]
        ])
    )
    logger.info("Отправлено сообщение с тестом")

    await asyncio.sleep(35)
    logger.info("Прошло 35 секунд, отправляю сообщение с оценкой")

    if not os.path.exists('like.jpg'):
        logger.error("Файл like.jpg не найден")
        await update.message.reply_text("Ошибка: изображение не найдено.")
        return
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
    logger.info("Отправлено сообщение с оценкой")

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_reply_markup(reply_markup=None)

    feedback_type = "лайк 👍🏻" if query.data == "like" else "дизлайк 👎🏼"

    feedback_message = (
        "📢 Человек @{} дал фидбэк: {}"
    ).format(query.from_user.username, feedback_type)

    try:
        if not SENT_GROUP_ID or not SENT_GROUP_ID.startswith('-'):
            logger.error("SENT_GROUP_ID не задан или не является числовым ID группы")
            await query.message.reply_text("Ошибка: ID группы не настроен. Обратитесь к администратору.")
            return
        await context.bot.send_message(
            chat_id=SENT_GROUP_ID,
            text=feedback_message
        )
        logger.info("Фидбэк отправлен в группу")
    except Exception as e:
        logger.error(f"Ошибка при отправке фидбэка в группу: {e}")
        await query.message.reply_text("Произошла ошибка, попробуйте позже.")
        return

    await query.message.reply_text("Спасибо за ответ⚡️ До скорых встреч!")

def main():
    logger.info(f"Запуск бота... BOT_TOKEN: {BOT_TOKEN}, SENT_GROUP_ID: {SENT_GROUP_ID}")
    logger.info(f"Файл hello.jpg существует: {os.path.exists('hello.jpg')}")
    logger.info(f"Файл like.jpg существует: {os.path.exists('like.jpg')}")
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не задан")
        return
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()
    except Exception as e:
        logger.error(f"Ошибка при создании приложения: {e}")
        return

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getchatid", get_chat_id))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_rating, pattern="^(like|dislike)$"))

    logger.info("🤖 Бот успешно запущен!")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Ошибка при запуске polling: {e}")

if __name__ == '__main__':
    main()
