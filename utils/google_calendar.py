# utils/google_calendar.py
import datetime
import os
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    token_path = 'token.pickle'
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    # Если токена нет или он невалидный, вернуть None, пусть этим займётся наш ConversationHandler
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    if not creds:
        # Нет токена, вернём None, чтобы выше по коду
        # обрабатывалось это состоянием Conversations
        return None

    service = build('calendar', 'v3', credentials=creds)
    return service

def add_event_to_calendar(summary, event_date, event_time, description, calendar_id='primary'):
    service = get_calendar_service()
    start_datetime = datetime.datetime.combine(event_date, event_time)
    end_datetime = start_datetime + datetime.timedelta(hours=1)

    event = {
        'summary': summary,
        'description': description if description else '',
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'UTC'
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'UTC'
        },
    }

    event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
    return event_result.get('htmlLink')
