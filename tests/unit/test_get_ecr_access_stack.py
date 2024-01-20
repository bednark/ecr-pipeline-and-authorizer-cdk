import aws_cdk as core
import aws_cdk.assertions as assertions

from get_ecr_access.get_ecr_access_stack import GetEcrAccessStack

# example tests. To run these tests, uncomment this file along with the example
# resource in get_ecr_access/get_ecr_access_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = GetEcrAccessStack(app, "get-ecr-access")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
