import json
import os
from abc import ABC, abstractmethod
from datetime import datetime

import feedparser
from notion_client import Client
from tradernet.PublicApiClient import PublicApiClient

from service.currency_service import CurrencyRatioResolver
from update.helper import format_time, rich_text, heading_2_block, paragraph_block, strip_link, expression, \
    meetings_database_page


class Update(ABC):
    def __init__(self):
        self.client = Client(auth=os.environ['NOTION_TOKEN'])

    @abstractmethod
    def run(self):
        pass

    def reset_block_children(self, block_id, updates):
        current_children = self.client.blocks.children.list(block_id=block_id)
        for child in current_children['results']:
            self.client.blocks.delete(block_id=child['id'])
        self.client.blocks.children.append(
            block_id=block_id,
            children=updates
        )


class Meeting(Update):
    def __init__(self):
        super().__init__()
        self.meetings = os.environ['MEETINGS']
        self.meeting_database_id = os.environ['MEETINGS_DATABASE']
        self.json_meetings = json.loads(self.meetings)

    def run(self):
        data = self.client.databases.query(database_id=self.meeting_database_id)
        for page in data['results']:
            self.client.pages.update(page_id=page['id'], archived=True)
        for meeting in self.json_meetings:
            self.client.pages.create(
                parent={'database_id': self.meeting_database_id},
                properties=meetings_database_page(meeting['title'], meeting['start_date'], meeting['end_date'])
            )


class ToDo(Update):
    def __init__(self):
        super().__init__()
        self.to_dos = os.environ['TO_DOS']
        self.to_dos_block_id = os.environ['TO_DOS_BLOCK']
        self.json_to_dos = json.loads(self.to_dos)

    def run(self):
        self.reset_block_children(
            block_id=self.to_dos_block_id,
            updates=self.chunk_blocks()
        )

    def chunk_blocks(self):
        return [
            paragraph_block('▶︎ ' + todo) for todo in self.json_to_dos
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
    def __init__(self):
        super().__init__()
        self.newsletter_block_id = os.environ['NEWSLETTER_BLOCK']
        self.feeds = os.environ['FEEDS']
        self.feeds_json = json.loads(self.feeds)

    def run(self):
        blocks = []
        for feed in self.feeds_json:
            result = feedparser.parse(feed)
            latest = result.entries[0]
            blocks.append(heading_2_block(f'🗞️ {latest.title}'))
            blocks.append(paragraph_block(strip_link(latest.description)))
            blocks.append(paragraph_block(content='🔗 Read on', link=latest.link))
        self.reset_block_children(
            block_id=self.newsletter_block_id,
            updates=blocks
        )


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
            equation=expression(f'\\${total_comma}')
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
            code=rich_text(self.parse_birthdays())
        )

    def parse_birthdays(self):
        birthday_date = datetime.fromisoformat(self.json_birthdays[0]['start_date'])
        days_left = (birthday_date.date() - datetime.today().date()).days
        header = f'# ⏳ In {str(days_left)} day(s) ⏳ #' if days_left > 0 else '# 🎉 Today 🎉 #'
        event_title = self.json_birthdays[0]['title']
        return f'{header}\n{event_title}'


class Investment(Update):
    def __init__(self):
        super().__init__()
        self.broker_block_id = os.environ['BROKER_BLOCK']
        self.profit_block_id = os.environ['PROFIT_BLOCK']
        self.investment_page_id = os.environ['INVESTMENT_PAGE']
        self.public_key = os.environ['TRADERNET_PUBLIC_KEY']
        self.private_key = os.environ['TRADERNET_PRIVATE_KEY']
        self.info = PublicApiClient(self.public_key, self.private_key, 2) \
            .sendRequest('getPositionJson')['result']['ps']

    def run(self):
        total_usd = self.count_usd_total()
        total_positions = self.count_positions_totals('s')
        total_profits = self.count_positions_totals('profit_close')
        total = total_positions + total_profits + total_usd
        self.update_investment_block(total, self.broker_block_id)
        self.update_investment_block(total_profits, self.profit_block_id)
        self.update_investment_page(total)

    def count_usd_total(self):
        return sum(
            map(
                lambda acc: acc['s'],
                filter(
                    lambda account: account['curr'] == 'USD',
                    self.info['acc']
                )
            )
        )

    def count_positions_totals(self, prop):
        return sum(
            map(
                lambda pos: pos[prop],
                self.info['pos']
            )
        )

    def update_investment_block(self, amount, block_id):
        amount_comma = '{:,}'.format(amount)
        self.client.blocks.update(
            block_id=block_id,
            equation=expression(f'\\${amount_comma}')
        )

    def update_investment_page(self, amount):
        self.client.pages.update(page_id=self.investment_page_id, properties={
            'Sum': {
                'number': amount
            }
        })


def main():
    updates = [
        Investment(),
        Budget(),
        Meeting(),
        ToDo(),
        Weather(),
        Birthday(),
        Headline()
    ]

    for update in updates:
        update.run()
