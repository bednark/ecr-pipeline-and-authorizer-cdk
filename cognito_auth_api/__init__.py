from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway
)
import aws_cdk as core
from constructs import Construct

class CognitoAuthAPI(Stack):
  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    ecr_auth_lambda = lambda_.Function(self,
      'PrivateECRAuthenticationLambda',
      handler = 'lambda_handler.lambda_handler',
      runtime = lambda_.Runtime.PYTHON_3_12,
      code = lambda_.Code.from_asset('lambda'),
      timeout = Duration.seconds(10)
    )

    ecr_auth_lambda.add_environment('CLIENT_ID', core.Fn.import_value('PrivateECRUserPoolAppId'))
    ecr_auth_lambda.add_environment('IDENTITY_ID', core.Fn.import_value('PrivateECRIdentityPoolId'))
    ecr_auth_lambda.add_environment('IDP_POOL', f'cognito-idp.eu-west-1.amazonaws.com/{core.Fn.import_value("PrivateECRUserPoolId")}')
    ecr_auth_lambda.add_environment('REGION', self.region)

    ecr_rest_api = apigateway.RestApi(self,
      'PrivateECRAuthenticationAPI',
      endpoint_types = [apigateway.EndpointType.REGIONAL]
    )

    auth_resource = ecr_rest_api.root.add_resource('auth')
    auth_resource.add_method('POST',
      integration = apigateway.LambdaIntegration(ecr_auth_lambda,
        proxy = False,
        passthrough_behavior = apigateway.PassthroughBehavior.WHEN_NO_TEMPLATES,
        integration_responses = [apigateway.IntegrationResponse(status_code = '200')]
      ),
      method_responses = [
        apigateway.MethodResponse(
          status_code = '200',
          response_models = {
              'application/json': apigateway.Model.EMPTY_MODEL
          }
        )
      ]
    )