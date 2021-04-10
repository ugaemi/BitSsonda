import json
import locale
import os
from datetime import *

import pyupbit
import requests


class BitSsonda:
    def __init__(self):
        self.db = {"date": datetime.now().strftime('%Y%m%d')}
        self.SLACK_URL = os.environ.get('SLACK_URL')

    def check_today(self, trade_date):
        db_date = self.db["date"]
        if db_date != trade_date:
            self.db = {"date": trade_date}

    def hooking(self, **data):
        code = data.get("code")
        change = data.get("change")
        trade_price = data.get("trade_price")
        signed_change_rate = data.get("signed_change_rate")

        if change == "RISE":
            db_rate = self.db.get(code)
            signed_change_rate = int(signed_change_rate * 100)

            if not signed_change_rate:
                return

            if db_rate and int(db_rate) >= signed_change_rate:
                return

            self.db[code] = signed_change_rate
            res = requests.post(
                self.SLACK_URL,
                data=json.dumps({"text": f"⏰ {datetime.now().strftime('%H:%M')} 🪙 {code} 📈 {signed_change_rate}% 💰 {int(trade_price):,}원"}),
                headers={"Content-Type": "application/json; charset=utf-8"}
            )

            if not res.status_code == 200:
                print(res.__dict__)

    def run(self):
        krw_tickers = pyupbit.get_tickers(fiat="KRW")
        wm = pyupbit.WebSocketManager("ticker", krw_tickers)

        while True:
            data = wm.get()
            print(data)
            trade_date = data.get("trade_date")
            self.check_today(trade_date)
            self.hooking(**data)


if __name__ == "__main__":
    print("App started!")
    locale.setlocale(locale.LC_ALL, '')
    cls = BitSsonda()
    cls.run()
