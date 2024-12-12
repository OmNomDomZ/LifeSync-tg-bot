# handlers/sync_calendar.py
import os
import pickle
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from google_auth_oauthlib.flow import InstalledAppFlow

from utils.db import list_events
from utils.google_calendar import add_event_to_calendar, SCOPES

EMAIL, WAITING_CODE = range(2)

async def start_sync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем есть ли уже токен:
    if os.path.exists('token.pickle'):
        # Токен есть, просто синхронизируем
        await sync_now(update, context)
        return ConversationHandler.END
    else:
        # Запросим email у пользователя, если действительно надо
        # Если вам email не нужен, можете пропустить этот шаг и сразу давать ссылку
        await update.message.reply_text("Для синхронизации с вашим календарём, введите ваш Google email (тот, под которым вы заходите в Google Calendar):")
        return EMAIL

async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_email = update.message.text.strip()
    context.user_data['user_email'] = user_email

    # Создаём flow
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')

    # Получаем URL авторизации
    auth_url, _ = flow.authorization_url(prompt='consent')

    # Сохраним flow в context, чтобы потом использовать
    context.user_data['flow'] = flow

    await update.message.reply_text(
        "Перейдите по ссылке ниже, разрешите доступ, затем скопируйте и пришлите сюда код авторизации:\n\n" + auth_url
    )
    return WAITING_CODE

async def receive_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    flow = context.user_data.get('flow')

    # Получаем токен по коду
    flow.fetch_token(code=code)
    creds = flow.credentials

    # Сохраняем токен
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

    await update.message.reply_text("Авторизация прошла успешно! Выполняю синхронизацию...")

    await sync_now(update, context)
    return ConversationHandler.END

async def sync_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    events = list_events(user_id)
    if not events:
        await update.message.reply_text("У вас нет событий для синхронизации.")
        return

    added_count = 0
    for e in events:
        add_event_to_calendar(
            summary=e['title'],
            event_date=e['event_date'],
            event_time=e['event_time'],
            description=e['description'],
            calendar_id='primary'
        )
        added_count += 1

    await update.message.reply_text(f"Синхронизация завершена. Добавлено {added_count} событий в календарь.")

async def cancel_sync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

def get_sync_conversation_handler():
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Синхронизировать с календарём$"), start_sync)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)],
            WAITING_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_code)],
        },
        fallbacks=[CommandHandler("cancel", cancel_sync)],
        name="sync_calendar_conversation",
        persistent=False
    )
