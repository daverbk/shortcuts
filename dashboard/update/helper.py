from datetime import datetime


def format_time(date_str):
    return datetime.fromisoformat(date_str).strftime(format('%H:%M'))


def rich_text_update(data):
    return {'rich_text': [{'text': {'content': data}}]}
