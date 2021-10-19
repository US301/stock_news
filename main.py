import requests
import os

from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient

# Stock Information
STOCK_API = os.environ["STOCK_API"]
STOCK = "TSLA"

ACCOUNT_SID = os.environ["ACCOUNT_SID"]
AUTH_TOKEN = os.environ["AUTH_TOKEN"]
PHONE_NUMBER = os.environ["PHONE_NUMBER"]

# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
stock_parameters = {

    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "outputsize": "compact",
    "apikey": STOCK_API,
}

URL = "https://www.alphavantage.co/query"
raw_stock_data = requests.get(URL, params=stock_parameters)
raw_stock_data.raise_for_status()
stock_data = raw_stock_data.json()["Time Series (Daily)"]
stock_index_today = list(stock_data)[0]
stock_index_yesterday = list(stock_data)[1]
closing_today = float(stock_data[stock_index_today]["4. close"])
closing_yesterday = float(stock_data[stock_index_yesterday]["4. close"])
percent_change = ((closing_today - closing_yesterday)/closing_yesterday) * 100
abs_percent_change = abs(percent_change)

# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 
URL = os.environ["URL"]
NEWS_API = os.environ["NEWS_API"]
COMPANY_NAME = "Tesla Inc"

news_parameters = {
    "apiKey": NEWS_API,
    "q": COMPANY_NAME,
    "category": "business",
    "country": "us",
}
raw_news = requests.get(URL, params=news_parameters)
raw_news.raise_for_status()
news_data = raw_news.json()

first_news_title = news_data["articles"][0]["title"]
first_news_description = news_data["articles"][0]["description"]
second_news_title = news_data["articles"][1]["title"]
second_news_description = news_data["articles"][1]["description"]

# Send a seperate message with the percentage change and each article's title and description to your phone number.

if percent_change > 0:
    symbol = "🔺"
elif percent_change < 0:
    symbol = "🔻"
else:
    symbol = " "

sms_message = f"""
TSLA: {symbol}{abs_percent_change}%
Headline: {first_news_title}. 
Brief: {first_news_description}.
"""

if abs_percent_change > 5:
    for article in news_data["articles"]:
        article_title = article["title"]
        article_message = article["description"]

        sms_message = f"""
        TSLA: {symbol}{abs_percent_change}%
        Headline: {article_title}. 
        Brief: {article_message}.
        """
        proxy_client = TwilioHttpClient()
        proxy_client.session.proxies = {'https': os.environ['https_proxy']}
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages \
            .create(
            body=sms_message,
            from_= PHONE_NUMBER,
            to='+16477205213'
        )
        print(message.status)




