import os

import httpx


class CurrencyResolver:
    frankfurter_url = os.environ['FRANKFURTER_URL']
    nb_rb_url = os.environ['NB_RB_URL']

    def resolve(self, currency):
        if currency in ['usd', 'eur']:
            return self.get_currency_ratio(currency)
        elif currency == 'byn':
            return self.get_byn_ratio()
        else:
            raise ValueError('Unknown currency')

    def get_currency_ratio(self, of):
        response = httpx.get(url=self.frankfurter_url, params={"from": of, "to": "usd"}).json()
        return response['rates']['USD']

    def get_byn_ratio(self):
        response = httpx.get(url=self.nb_rb_url, params={"parammode": 2}).json()
        return 1 / response['Cur_OfficialRate']
