from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler

from utils.db import delete_event

DELETE_ID = range(1)

async def start_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ID события для удаления или /cancel для отмены:")
    return DELETE_ID

async def receive_delete_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.isdigit():
        event_id = int(text)
        user_id = update.effective_user.id
        result = delete_event(user_id, event_id)
        if result > 0:
            await update.message.reply_text("Событие успешно удалено!")
        else:
            await update.message.reply_text("Событие с таким ID не найдено.")
    else:
        await update.message.reply_text("Неверный формат ID. Введите число или /cancel для отмены.")
    return ConversationHandler.END

async def cancel_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Удаление отменено.")
    return ConversationHandler.END

def get_delete_conversation_handler():
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Удалить событие$"), start_delete)],
        states={
            DELETE_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_delete_id)]
        },
        fallbacks=[CommandHandler("cancel", cancel_delete)],
        name="delete_event_conversation",
        persistent=False
    )
