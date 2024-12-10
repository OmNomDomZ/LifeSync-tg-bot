from telegram import Update
from telegram.ext import ContextTypes

from utils.db import list_events


async def list_user_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    events = list_events(user_id)
    if not events:
        await update.message.reply_text("У вас нет событий.")
    else:
        response = "\n".join([
            f"{e['id']}: {e['title']} - {e['event_date']} {e['event_time']} {(e['description'] if e['description'] else '')}"
            for e in events
        ])
        await update.message.reply_text(response)
