"""
Lambda to get data fom API and store them in dynamoDB
"""

import boto3
import os
from boto3.dynamodb.conditions import Key
from utils import coingecko
from utils import run_id
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PriceStore')

def handle(event, context):
    print('event: ', event)
    print('context:', context)

    id_run = run_id.generate_run_id()

    # get symbols
    API_IDS = str(os.environ['SYMBOLS'])

    if not coingecko.check_status() :
        raise Exception(f'API server is down, run id: {id_run}')

    # query coingecko api
    symbol_data = coingecko.fetch_price_data_by_symbol(API_IDS)

    print(f'fetched data: {symbol_data} run id: {id_run}')

    for symbol in symbol_data: # iterate over symbol ids
        id_symbol = symbol

        # create update expression
        expression, values = get_update_params({
            'price_usd': Decimal(str(symbol_data[symbol]['usd'])), # must use decimal
            'market_cap_usd': Decimal(str(symbol_data[symbol]['usd_market_cap'])),
            'volume_24h_usd': Decimal(str(symbol_data[symbol]['usd_24h_vol']))
        })

        # insert or update to table
        response = table.update_item(
            Key={'id_symbol':str(id_symbol)},
            UpdateExpression=expression,
            ExpressionAttributeValues=dict(values)
        )

        print(f'update response: {response} for: {id_symbol} run id: {id_run}')

def get_update_params(body):
    update_expression = ["set "]
    update_values = dict()

    for k, v in body.items():
        update_expression.append(f" {k} = :{k},")
        update_values[f":{k}"] = v

    return "".join(update_expression)[:-1], update_values