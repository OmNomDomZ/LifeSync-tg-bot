from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler, CallbackQueryHandler
import datetime

from utils.db import add_event

TITLE, SELECT_DATE, SELECT_TIME, DESCRIPTION = range(4)
DATE_ADJUST, TIME_ADJUST = range(2)  # состояния для callback в date/time

# Шаг 1: Ввод названия
async def start_create_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите название события или /cancel для отмены:")
    return TITLE

async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text.strip()
    context.user_data["new_event_title"] = title

    # Начальные значения даты - сегодня
    context.user_data["temp_date"] = datetime.date.today()
    await show_date_picker(update, context)
    return SELECT_DATE

def make_date_keyboard(d):
    buttons = [
        [
            InlineKeyboardButton("<< Год", callback_data="YEAR_DOWN"),
            InlineKeyboardButton(d.strftime("%Y"), callback_data="YEAR_NOP"),
            InlineKeyboardButton("Год >>", callback_data="YEAR_UP")
        ],
        [
            InlineKeyboardButton("<< Месяц", callback_data="MONTH_DOWN"),
            InlineKeyboardButton(d.strftime("%m"), callback_data="MONTH_NOP"),
            InlineKeyboardButton("Месяц >>", callback_data="MONTH_UP")
        ],
        [
            InlineKeyboardButton("<< День", callback_data="DAY_DOWN"),
            InlineKeyboardButton(d.strftime("%d"), callback_data="DAY_NOP"),
            InlineKeyboardButton("День >>", callback_data="DAY_UP")
        ],
        [InlineKeyboardButton("Готово", callback_data="DATE_DONE")]
    ]
    return InlineKeyboardMarkup(buttons)

async def show_date_picker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data["temp_date"]
    if update.callback_query:
        query = update.callback_query
        await query.edit_message_text("Выберите дату:", reply_markup=make_date_keyboard(d))
        await query.answer()
    else:
        await update.message.reply_text("Выберите дату:", reply_markup=make_date_keyboard(d))

async def date_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    d = context.user_data["temp_date"]

    if query.data == "YEAR_UP":
        d = datetime.date(d.year+1, d.month, d.day)
    elif query.data == "YEAR_DOWN":
        d = datetime.date(d.year-1, d.month, d.day)
    elif query.data == "MONTH_UP":
        new_month = d.month + 1
        new_year = d.year
        if new_month > 12:
            new_month = 1
            new_year += 1
        # корректируем день, если превышает кол-во дней в месяце
        max_day = (datetime.date(new_year, new_month, 28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
        day = min(d.day, max_day.day)
        d = datetime.date(new_year, new_month, day)
    elif query.data == "MONTH_DOWN":
        new_month = d.month - 1
        new_year = d.year
        if new_month < 1:
            new_month = 12
            new_year -= 1
        max_day = (datetime.date(new_year, new_month, 28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
        day = min(d.day, max_day.day)
        d = datetime.date(new_year, new_month, day)
    elif query.data == "DAY_UP":
        d = d + datetime.timedelta(days=1)
    elif query.data == "DAY_DOWN":
        d = d - datetime.timedelta(days=1)
    elif query.data == "DATE_DONE":
        # Дата выбрана
        context.user_data["new_event_date"] = d
        # Теперь выбираем время
        context.user_data["temp_hour"] = 12
        context.user_data["temp_minute"] = 0
        await show_time_picker(query, context)
        return SELECT_TIME

    context.user_data["temp_date"] = d
    await show_date_picker(update, context)
    return SELECT_DATE

def make_time_keyboard(hour, minute):
    buttons = [
        [
            InlineKeyboardButton("Час--", callback_data="HOUR_DOWN"),
            InlineKeyboardButton("Час++", callback_data="HOUR_UP")
        ],
        [
            InlineKeyboardButton(f"{hour:02d}:{minute:02d}", callback_data="TIME_NOP"),
        ],
        [
            InlineKeyboardButton("Мин--", callback_data="MIN_DOWN"),
            InlineKeyboardButton("Мин++", callback_data="MIN_UP")
        ],
        [InlineKeyboardButton("Готово", callback_data="TIME_DONE")]
    ]
    return InlineKeyboardMarkup(buttons)

async def show_time_picker(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    hour = context.user_data["temp_hour"]
    minute = context.user_data["temp_minute"]

    if hasattr(update_or_query, 'edit_message_text'):
        # Это CallbackQuery
        await update_or_query.edit_message_text("Выберите время:", reply_markup=make_time_keyboard(hour, minute))
    else:
        # Это сообщение
        await update_or_query.message.reply_text("Выберите время:", reply_markup=make_time_keyboard(hour, minute))

async def time_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    hour = context.user_data["temp_hour"]
    minute = context.user_data["temp_minute"]

    if query.data == "HOUR_UP":
        hour = (hour + 1) % 24
    elif query.data == "HOUR_DOWN":
        hour = (hour - 1) % 24
    elif query.data == "MIN_UP":
        minute = (minute + 15) % 60
    elif query.data == "MIN_DOWN":
        minute = (minute - 15) % 60
    elif query.data == "TIME_DONE":
        # Время выбрано
        context.user_data["new_event_time"] = datetime.time(hour, minute)
        await query.edit_message_text("Введите описание события ('-' чтобы оставить пустым) или /cancel для отмены:")
        return DESCRIPTION

    context.user_data["temp_hour"] = hour
    context.user_data["temp_minute"] = minute
    await show_time_picker(query, context)
    return SELECT_TIME

async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.text and not(update.message.text == '-'):
        description = update.message.text.strip()
    else:
        description = None

    user_id = update.effective_user.id
    title = context.user_data.get("new_event_title")
    event_date = context.user_data.get("new_event_date")
    event_time = context.user_data.get("new_event_time")

    event_id = add_event(user_id, title, event_date, event_time, description)
    await update.message.reply_text(f"Событие успешно создано! ID: {event_id}")

    context.user_data.clear()

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    context.user_data.clear()
    return ConversationHandler.END

def get_create_conversation_handler():
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Создать событие$"), start_create_event)],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],
            SELECT_DATE: [CallbackQueryHandler(date_callback)],
            SELECT_TIME: [CallbackQueryHandler(time_callback)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="create_event_conversation",
        persistent=False
    )
