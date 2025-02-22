import json
import os
import textwrap
from abc import ABC, abstractmethod
from datetime import date, datetime

from notion_client import Client

from service.currency_service import CurrencyRatioResolver
from update.helper import format_time, rich_text_update


class Update(ABC):
    def __init__(self):
        self.client = Client(auth=os.environ['NOTION_TOKEN'])

    @abstractmethod
    def run(self):
        pass


class Meeting(Update):
    def __init__(self):
        super().__init__()
        self.meetings = os.environ['MEETINGS']
        self.meetings_block_id = os.environ['MEETINGS_BLOCK']
        self.json_meetings = json.loads(self.meetings)

    def run(self):
        self.client.blocks.update(
            block_id=self.meetings_block_id,
            code=rich_text_update(self.parse_meetings())
        )

    def parse_meetings(self):
        result = ''
        if self.json_meetings:
            for meeting in self.json_meetings:
                result += f'''
                # {meeting['title']} #
                {format_time(meeting['start_date'])} - {format_time(meeting['end_date'])}
            '''
        else:
            result = '# 🤘 No meetings for today! Hooray! 🙂‍↕️ #'
        return textwrap.dedent(result).rstrip('\r\n')


class ToDo(Update):
    def __init__(self):
        super().__init__()
        self.to_dos = os.environ['TO_DOS']
        self.to_dos_block_id = os.environ['TO_DOS_BLOCK']
        self.json_to_dos = json.loads(self.to_dos)

    def run(self):
        current_children = self.client.blocks.children.list(block_id=self.to_dos_block_id)
        for child in current_children['results']:
            self.client.blocks.delete(block_id=child['id'])
        self.client.blocks.children.append(
            block_id=self.to_dos_block_id,
            children=self.chunk_blocks()
        )

    def chunk_blocks(self):
        return [
            {'object': 'block', 'type': 'to_do',
             'to_do': {'rich_text': [{'type': 'text', 'text': {'content': todo}}], 'checked': False}}
            for todo in self.json_to_dos
        ]


class Weather(Update):
    def __init__(self):
        super().__init__()
        self.weather_row_id = os.environ['WEATHER_ROW']
        self.weather = os.environ['WEATHER']
        self.weather_json = json.loads(self.weather)

    def run(self):
        def text_update(content):
            return [{'text': {'content': content}}]

        self.client.blocks.update(
            block_id=self.weather_row_id,
            table_row={
                'cells': [
                    text_update(str(self.weather_json['max'])),
                    text_update(str(self.weather_json['min'])),
                    text_update(format_time(self.weather_json['sunrise'])),
                    text_update(format_time(self.weather_json['sunset']))
                ]
            }
        )


class Headline(Update):
    def run(self):
        pass


class Habit(Update):
    def __init__(self):
        super().__init__()
        self.habits_database_id = os.environ['HABITS_DB']
        self.habits_block_id = os.environ['HABITS_BLOCK']

    def run(self):
        habits_db = self.client.databases.query(database_id=self.habits_database_id, filter={
            'property': 'Created time', 'date': {'on_or_before': date.today().isoformat()}
        })
        today_id = habits_db['results'][0]['id']
        self.client.blocks.update(block_id=self.habits_block_id, callout={
            'rich_text': [{'mention': {'page': {'id': today_id}}}]
        })


class Budget(Update):
    currencies = {
        'pln': 'PlnUsdRate',
        'eur': 'EurUsdRate',
        'byn': 'BynUsdRate'
    }

    def __init__(self):
        super().__init__()
        self.budget_page_id = os.environ['BUDGET_PAGE']
        self.budget_db_id = os.environ['BUDGET_DB']
        self.budget_block_id = os.environ['BUDGET_BLOCK']
        self.currency_rate_resolver = CurrencyRatioResolver()

    def run(self):
        for currency in self.currencies:
            self.update_currency_rate(currency)
        self.drag_total_to_dashboard()

    def update_currency_rate(self, currency):
        ratio = self.currency_rate_resolver.resolve(currency)
        self.client.pages.update(page_id=self.budget_page_id, properties={
            self.currencies[currency]: {
                'number': ratio
            }
        })

    def drag_total_to_dashboard(self):
        budget_data = self.client.databases.query(database_id=self.budget_db_id)
        total = budget_data['results'][0]['properties']['Total']['formula']['number']
        total_comma = '{:,}'.format(total)
        self.client.blocks.update(
            block_id=self.budget_block_id,
            code=rich_text_update(f'# $ {total_comma} #')
        )


class Birthday(Update):
    def __init__(self):
        super().__init__()
        self.birthdays = os.environ['BIRTHDAYS']
        self.birthdays_block_id = os.environ['BIRTHDAYS_BLOCK']
        self.json_birthdays = json.loads(self.birthdays)

    def run(self):
        self.client.blocks.update(
            block_id=self.birthdays_block_id,
            code=rich_text_update(self.parse_birthdays())
        )

    def parse_birthdays(self):
        birthday_date = datetime.fromisoformat(self.json_birthdays[0]['start_date'])
        days_left = (birthday_date.date() - datetime.today().date()).days
        header = f'# ⏳ In {str(days_left)} day(s) ⏳ #' if days_left > 0 else '# 🎉 Today 🎉 #'
        event_title = self.json_birthdays[0]['title']
        return f'{header}\n{event_title}'


def main():
    updates = [
        Budget(),
        Meeting(),
        ToDo(),
        Habit(),
        Weather(),
        Birthday(),
        Headline()
    ]

    for update in updates:
        update.run()
