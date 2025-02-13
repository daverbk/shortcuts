import os
from abc import ABC, abstractmethod

import httpx
from notion_client import Client


class Update(ABC):
    def __init__(self):
        self.client = Client(auth=os.environ["NOTION_TOKEN"])

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

    budget_page_id = os.environ["BUDGET_PAGE"]
    ratios = {
        "pln": "PlnUsdRate",
        "eur": "EurUsdRate"
    }

    def run(self):
        # Get currency data from an external api
        # Update the rates on the budgeting page

        # Byn -> Usd
        # Eur -> Usd
        # Pln -> Usd

        for ratio in self.ratios:
            self.update_currency_rate(ratio)

        # Update the total on the dashboard page

        pass

    def update_currency_rate(self, of):
        update = {
            self.ratios[of]: {
                "number": "asdf"
            }
        }
        self.client.pages.update(page_id=self.budget_page_id, properties=update)

class Birthday(Update):
    def run(self):
        pass
