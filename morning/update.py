import os
from abc import ABC, abstractmethod

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
    def run(self):
        pass


class Budget(Update):
    budget_page_id = os.environ['BUDGET_PAGE']
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
        # Update the total on the dashboard page

    def update_currency_rate(self, currency):
        ratio = self.currency_rate_resolver.resolve(currency)
        self.client.pages.update(page_id=self.budget_page_id, properties={
            self.currencies[currency]: {
                'number': ratio
            }
        })


class Birthday(Update):
    def run(self):
        pass
