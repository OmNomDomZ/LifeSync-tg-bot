from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Доступные команды и действия:\n"
        "/start - Начать работу с ботом\n"
        "/help - Вывести это сообщение\n"
        "/cancel - Отменить текущее действие\n\n"
        "Кнопки:\n"
        "Создать событие:\n"
        "  1) Введите название\n"
        "  2) Выберите дату (кнопками)\n"
        "  3) Выберите время (кнопками)\n"
        "  4) Введите описание\n"
        "Просмотреть события - покажет список\n"
        "Удалить событие - удалит событие по его ID\n"
        "Помощь - эта справка\n\n"
        "Используйте /cancel для отмены операции."
    )
    await update.message.reply_text(help_text)
