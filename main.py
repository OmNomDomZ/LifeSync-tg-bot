import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from handlers.start import start
from handlers.help import help_command
from handlers.create import get_create_conversation_handler
from handlers.list_events import list_user_events
from handlers.delete_event import get_delete_conversation_handler

from config import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Отдельно кнопка "Помощь"
    app.add_handler(MessageHandler(filters.Regex("^Помощь$"), help_command))

    # Конверсационные хендлеры
    app.add_handler(get_create_conversation_handler())
    app.add_handler(get_delete_conversation_handler())

    # Просмотр событий
    app.add_handler(MessageHandler(filters.Regex("^Просмотреть события$"), list_user_events))

    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
