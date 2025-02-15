import os
from abc import ABC, abstractmethod
from datetime import date

from notion_client import Client


class Update(ABC):
    def __init__(self):
        self.client = Client(auth=os.environ['NOTION_TOKEN'])

    @abstractmethod
    def run(self):
        pass


class Meeting(Update):
    def run(self):
        pass


class ToDo(Update):
    def run(self):
        pass


class Weather(Update):
    def run(self):
        pass


class Headline(Update):
    def run(self):
        pass


class Habit(Update):
    habits_database_id = os.environ['HABITS_DB']
    habits_block_id = os.environ['HABITS_BLOCK']

    def run(self):
        habits_db = self.client.databases.query(database_id=self.habits_database_id, filter={
            'property': "Created time",
            'date': {
                'on_or_after': date.today().isoformat()
            }
        })
        today_id = habits_db['results'][0]['id']
        self.client.blocks.update(block_id=self.habits_block_id, callout={
            'rich_text': [{'mention': {'page': {'id': today_id}}}]
        })


class Budget(Update):
    budget_page_id = os.environ['BUDGET_PAGE']
    budget_db_id = os.environ['BUDGET_DB']
    budget_block_id = os.environ['BUDGET_BLOCK']
    currencies = {
        'pln': 'PlnUsdRate',
        'eur': 'EurUsdRate',
        'byn': 'BynUsdRate'
    }

    def __init__(self):
        super().__init__()
        from service import CurrencyRatioResolver
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
        self.client.blocks.update(block_id=self.budget_block_id, code={
            'rich_text': [{'text': {'content': "# " + total_comma + " #"}}]
        })


class Birthday(Update):
    def run(self):
        pass
