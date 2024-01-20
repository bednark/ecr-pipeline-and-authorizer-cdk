from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_
)
import aws_cdk as core
from constructs import Construct

class CognitoAuthAPI(Stack):
  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    ecr_auth_lambda = lambda_.Function(self,
      'PrivateECRAuthenticationLambda',
      handler = 'lambda_handler.handler',
      runtime = lambda_.Runtime.PYTHON_3_12,
      code = lambda_.Code.from_asset('lambda'),
      timeout = Duration.seconds(10)
    )

    ecr_auth_lambda.add_environment('CLIENT_ID', core.Fn.import_value('PrivateECRUserPoolAppId'))
    ecr_auth_lambda.add_environment('IDENTITY_ID', core.Fn.import_value('PrivateECRIdentityPoolId'))
    ecr_auth_lambda.add_environment('IDP_POOL', f'cognito-idp.eu-west-1.amazonaws.com/{core.Fn.import_value('PrivateECRUserPoolId')}')
    ecr_auth_lambda.add_environment('REGION', self.region)