"""
Lambda that will subscribe user to sns topic
"""

import os
import boto3
import json
import re

sns = boto3.client('sns')

def handle(event, context):
    print('event: ', event)
    print('context:', context)

    topic_arn = str(os.environ["SNS_ARN"])

    # get the email address from the event
    email = json.loads(event['body'])['email']

    # check if email is valid
    if not email or not is_valid_email(email):
        return {
            'statusCode': 400,
            'body': 'Please provide a valid email address'
        }

    print(f'subscribing {email} to the SNS topic')

    # subscribe the email address to the SNS topic
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=email
    )

    # subscribe webhok to the SNS topic
    # sns.subscribe(
    #     TopicArn=topic_arn,
    #     Protocol='https',
    #     Endpoint='https://webhook.site/9b9b9b9b-9b9b-9b9b-9b9b-9b9b9b9b9b9b'
    # )

    return {
        'statusCode': 200,
        'body': 'Successfully subscribed {} to the SNS topic'.format(email)
    }

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None