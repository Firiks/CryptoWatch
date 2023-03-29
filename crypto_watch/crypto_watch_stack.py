"""
Define stack
"""

import os
from dotenv import load_dotenv
from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as _alambda,
    aws_lambda_event_sources as _lambda_event_sources,
    aws_dynamodb as _dynamodb,
    aws_events as _events,
    aws_events_targets as _events_targets,
    aws_sqs as _sqs,
    aws_sns as _sns,
    aws_sns_subscriptions as _sns_subscription,
    aws_logs as _logs,
    # aws_ec2 as _ec2,
    # aws_efs as _efs
)
from constructs import Construct

# read .env files
load_dotenv()

class CryptoWatchStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        """
        Constants
        """

        SYMBOLS= os.getenv('SYMBOLS') # symbols to watch
        CHANGE= os.getenv('CHANGE') # % change to send message
        EVENT_INTERVAL_MINUTES = os.getenv('EVENT_INTERVAL_MINUTES') # EventBridge interval in minutes
        EMAIL = os.getenv('EMAIL') # email to send notification
        TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY') # Telegram bot API key
        TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') # Telegram chat ID
        DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK') # Discord

        """
        DynamoDB
        """

        # DynamoDB crate table
        table = _dynamodb.Table(self, "PriceStore",
            table_name="PriceStore",
            partition_key=_dynamodb.Attribute(
                name="id_symbol", 
                type=_dynamodb.AttributeType.STRING
            ),
            billing_mode=_dynamodb.BillingMode.PROVISIONED,
            # replication_regions=['eu-west-1', 'eu-west-2', 'eu-west-3'], # uncoment to enable scaling across multiple regions
            table_class=_dynamodb.TableClass.STANDARD,
            stream=_dynamodb.StreamViewType.NEW_AND_OLD_IMAGES, # get old and new data in stream
            write_capacity=1,
            read_capacity=1
        )

        # uncoment to enable scaling across multiple regions
        # read scaling
        # table.auto_scale_read_capacity(
        #     min_capacity=1,
        #     max_capacity=10
        # ).scale_on_utilization(target_utilization_percent=75)

        # write scaling
        # table.auto_scale_write_capacity(
        #     min_capacity=1,
        #     max_capacity=10
        # ).scale_on_utilization(target_utilization_percent=75)

        """
        SQS
        """

        # SQS for DLQ
        cryptoWatchSQS = _sqs.Queue(self, "CryptoWatchSQS", queue_name="CryptoWatchSQS", retention_period=Duration.days(3))

        """
        SNS
        """

        # Create topic
        topic = _sns.Topic(self, "CryptowatchTopic",
            display_name="Cryptowatch subscription topic"
        )

        # Subscribers
        # topic.add_subscription(_sns_subscription.UrlSubscription("https://example.com/")) # url
        topic.add_subscription(_sns_subscription.EmailSubscription(EMAIL, json=False)) # email

        """
        IAM
        """

        # Create the IAM role for the Lambda function
        role = _iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com")
        )

        role.add_to_policy(
            _iam.PolicyStatement(
                actions=["sns:Subscribe"],
                resources=[topic.topic_arn]
            )
        )

        """
        Lambda
        """

        # Fetch Data Lambda
        fetchDataFunction = _alambda.PythonFunction(
            self,
            "FetchDataFn",
            entry="./lambda/",
            runtime=_lambda.Runtime.PYTHON_3_9,
            index="fetch_data.py",
            handler="handle",
            reserved_concurrent_executions=10,
            dead_letter_queue_enabled=True,
            dead_letter_queue=cryptoWatchSQS,
            log_retention=_logs.RetentionDays.THREE_DAYS,
            environment={
                "SYMBOLS": SYMBOLS
            },
            timeout=Duration.seconds(2),
            # tracing=_lambda.Tracing.ACTIVE, # enable xray tracing
            description="Fetch data from CoinGecko API"
        )

        # Notify SNS Lambda
        notifySNSFunction = _alambda.PythonFunction(
            self,
            "NotifySNSFn",
            entry="./lambda/",
            runtime=_lambda.Runtime.PYTHON_3_9,
            index="notify_sns.py",
            handler="handle",
            reserved_concurrent_executions=10,
            dead_letter_queue_enabled=True,
            dead_letter_queue=cryptoWatchSQS,
            log_retention=_logs.RetentionDays.THREE_DAYS,
            environment={
                "SNS_ARN": topic.topic_arn,
                "CHANGE": CHANGE,
                "TELEGRAM_API_KEY": TELEGRAM_API_KEY,
                "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
                "DISCORD_WEBHOOK": DISCORD_WEBHOOK
            },
            timeout=Duration.seconds(2),
            # tracing=_lambda.Tracing.ACTIVE, # enable xray tracing
            description="Notify SNS topic"
        )

        # Add subscriber Lambda
        subscribeUserFunction = _alambda.PythonFunction(
            self,
            "SubsribeUSerFn",
            entry="./lambda/",
            runtime=_lambda.Runtime.PYTHON_3_9,
            index="subscribe_user.py",
            handler="handle",
            reserved_concurrent_executions=10,
            dead_letter_queue_enabled=True,
            dead_letter_queue=cryptoWatchSQS,
            log_retention=_logs.RetentionDays.THREE_DAYS,
            environment={
                "SNS_ARN": topic.topic_arn,
            },
            timeout=Duration.seconds(1),
            # tracing=_lambda.Tracing.ACTIVE, # enable xray tracing
            role=role,
            description="Subscribe user to SNS topic"
        )

        """
        DynamoDB Streams
        """

        # Invoke notifySNSFunction using DynamoDB Stream
        notifySNSFunction.add_event_source(_lambda_event_sources.DynamoEventSource(
            table,
            starting_position=_lambda.StartingPosition.TRIM_HORIZON, # start from the beginning
            batch_size=5, # number of records to process in a batch
            bisect_batch_on_error=True,
            on_failure=_lambda_event_sources.SqsDlq(cryptoWatchSQS),
            retry_attempts=3, # number of times to retry
        ))

        """
        EventBridge
        """

        # Create event rule
        eventRule = _events.Rule(
            self,
            'EventRuleCryptowatch',
            # schedule= _events.Schedule.rate(Duration.minutes(int(EVENT_INTERVAL_MINUTES))) # every x min
            schedule = _events.Schedule.cron( # use cron expression
                minute=str(EVENT_INTERVAL_MINUTES),
            )
        )

        # Invoke fetchDataFunction
        eventRule.add_target( _events_targets.LambdaFunction(fetchDataFunction) )

        """
        Function URL
        """

        # Create function url
        function_url = subscribeUserFunction.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE,
            cors=_lambda.FunctionUrlCorsOptions(
                allowed_origins=["*"],
                allowed_methods=[_lambda.HttpMethod.POST],
                max_age=Duration.minutes(1)
            )
        )

        """
        Permissions
        """

        # SQS permissions
        cryptoWatchSQS.grant_send_messages(fetchDataFunction)
        cryptoWatchSQS.grant_send_messages(notifySNSFunction)
        cryptoWatchSQS.grant_send_messages(subscribeUserFunction)

        # DynamoDB permissions
        table.grant_read_write_data(fetchDataFunction)
        table.grant_stream_read(notifySNSFunction)

        # SNS permissions
        topic.grant_publish(notifySNSFunction)

        """
        Outputs
        """

        CfnOutput(self, "SubscribeUserFunctionURL",
            # The .url attributes will return the unique Function URL
            value=function_url.url,
            description="Subscribe user function URL",
            export_name="SubscribeUserFunctionURL"
        )
