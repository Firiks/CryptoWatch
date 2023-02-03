import aws_cdk as core
import aws_cdk.assertions as assertions

from crypto_watch.crypto_watch_stack import CryptoWatchStack

# example tests. To run these tests, uncomment this file along with the example
# resource in crypto_watch/crypto_watch_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CryptoWatchStack(app, "crypto-watch")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
