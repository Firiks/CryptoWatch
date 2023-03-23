"""
Lambda that is invoked by dynamoDB stream
"""

import os
import boto3
import requests
import urllib.parse
from utils import run_id

sns_client = boto3.client('sns')

def handle(event, context):
    print('event: ', event)
    print('context:', context)

    id_run = run_id.generate_run_id()

    for record in event['Records']:
        if 'OldImage' in record['dynamodb']: # check if we have old data
            old_image = record['dynamodb']['OldImage']
            new_image = record['dynamodb']['NewImage']
            symbol = str(new_image['id_symbol']['S'])

            percent_diff = abs(( (float(old_image['price_usd']['N']) - float(new_image['price_usd']['N'])) * 100 ) / float(old_image['price_usd']['N'])) # calculate % diff

            print(f'percent diff {str(percent_diff)} for symbol {symbol}, run id: {id_run}')

            # get enviroment values
            topic_arn = str(os.environ["SNS_ARN"])
            change = float(os.environ["CHANGE"])

            if float(percent_diff) >= change: # check if percentage reached threshold
                if new_image['price_usd']['N'] < old_image['price_usd']['N']:
                    percent_diff = percent_diff * (-1)

                message = build_message(percent_diff , new_image)
                subject = f"CryptoWatch price notification- {symbol}"

                print(f'sending notification for {symbol}, run id: {id_run}')

                # sns send email
                sns_client.publish(TopicArn=topic_arn, Message=message, Subject=subject)

                # telegram webhook
                notify_telegram(message)

                # discord webhook
                notify_discord(message)

def build_message(percent_diff , new_image):
    message = """
    Price notification

    Symbol : {symbol}/USD

    Change          :   {diff}%
    Price           :   {price} USD
    Market cap      :   {usd_market_cap} USD
    Volume 24H      :   {usd_24h_vol} USD

    """.format(symbol = str(new_image['id_symbol']['S']), diff = str(percent_diff), price = str(new_image['price_usd']['N']), usd_market_cap = str(new_image['market_cap_usd']['N']), usd_24h_vol = str(new_image['volume_24h_usd']['N']))

    return message

def notify_telegram(message):
    # use https://t.me/BotFather to generate new bot
    api_key = str(os.environ["TELEGRAM_API_KEY"])
    chat_id = str(os.environ["TELEGRAM_CHAT_ID"])

    message = urllib.parse.quote(message)

    send_data = 'https://api.telegram.org/bot' + api_key + '/sendMessage?chat_id=' + chat_id + '&parse_mode=MarkdownV2&text=' + message
    response = requests.get(send_data)

    print('Telegram webhook response:' ,response.json())


def notify_discord(message):
    # generate webhook in channel -> webhooks -> create webhook
    webhook_url = str(os.environ['DISCORD_WEBHOOK'])

    data = {"content": message}
    response = requests.post(webhook_url, json=data)

    print('Discord webhook response:' , response.json())
