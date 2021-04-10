import json
import locale
from datetime import *

import pyupbit
import requests
import redis


SLACK_URL = "https://hooks.slack.com/services/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"


def check_today(trade_date):
    db_date = rd.get("date")
    if db_date:
        db_date = db_date.decode('utf-8')
    if db_date != trade_date:
        rd.flushall()
        rd.set("date", trade_date)


def slack_webhook(**data):
    code = data.get("code")
    change = data.get("change")
    trade_price = data.get("trade_price")
    signed_change_rate = data.get("signed_change_rate")

    if change == "RISE":
        db_rate = rd.get(code)
        signed_change_rate = int(signed_change_rate * 100)

        if not signed_change_rate:
            return

        if db_rate and int(db_rate) >= signed_change_rate:
            return

        rd.set(code, signed_change_rate)
        res = requests.post(
            SLACK_URL,
            data=json.dumps({"text": f"⏰ {datetime.now().strftime('%H:%M')} 🪙 {code} 📈 {signed_change_rate}% 💰 {int(trade_price):,}원"}),
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

        if not res.status_code == 200:
            print(res.__dict__)


def upbit_ws_client():
    locale.setlocale(locale.LC_ALL, '')
    krw_tickers = pyupbit.get_tickers(fiat="KRW")
    wm = pyupbit.WebSocketManager("ticker", krw_tickers)

    while True:
        data = wm.get()
        trade_date = data.get("trade_date")
        check_today(trade_date)
        slack_webhook(**data)


if __name__ == "__main__":
    rd = redis.StrictRedis(host='localhost', port=6379, db=0)
    upbit_ws_client()
