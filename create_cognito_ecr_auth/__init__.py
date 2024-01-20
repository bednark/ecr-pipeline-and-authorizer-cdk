from aws_cdk import (
    Stack,
    Duration,
    aws_cognito as cognito,
    aws_iam as iam
)
import aws_cdk as core
from constructs import Construct

class CreateCognitoECRAuth(Stack):
  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    ecr_auth_user = cognito.UserPool(self, 'PrivateECRUserPool',
      sign_in_aliases = cognito.SignInAliases(username=True),
      password_policy = cognito.PasswordPolicy(
        min_length = 20,
        temp_password_validity=Duration.days(60)
      ),
      account_recovery = cognito.AccountRecovery.NONE,
      email = cognito.UserPoolEmail.with_cognito()
    )

    core.CfnOutput(self, 'PrivateECRUserPoolId',
      value = ecr_auth_user.user_pool_id,
      export_name = 'PrivateECRUserPoolId'
    )

    ecr_auth_user_client = ecr_auth_user.add_client('PrivateECRUserPoolApp',
      auth_flows = cognito.AuthFlow(
        user_password = True
      ),
      refresh_token_validity = Duration.hours(1),
      read_attributes = cognito.ClientAttributes().with_standard_attributes(email = True),
      write_attributes = cognito.ClientAttributes().with_standard_attributes(email = True),
      disable_o_auth = True
    )

    core.CfnOutput(self, 'PrivateECRUserPoolAppId',
      value = ecr_auth_user_client.user_pool_client_id,
      export_name = 'PrivateECRUserPoolAppId'
    )

    ecr_auth_identity = cognito.CfnIdentityPool(self, 'PrivateECRIdentityPool',
      allow_unauthenticated_identities = False,
      cognito_identity_providers = [
        cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
          client_id = ecr_auth_user_client.user_pool_client_id,
          provider_name = ecr_auth_user.user_pool_provider_name
        )
      ]
    )

    core.CfnOutput(self, 'PrivateECRIdentityPoolId',
      value = ecr_auth_identity.ref,
      export_name = 'PrivateECRIdentityPoolId'
    )

    cognito_policy = iam.ManagedPolicy(self, 'PrivateECRIdentityPoolPolicy',
      statements = [
        iam.PolicyStatement(
          actions = ['cognito-identity:GetCredentialsForIdentity'],
          resources = ['*']
        ),
        iam.PolicyStatement(
          actions = [
            'ecr:GetDownloadUrlForLayer',
            'ecr:BatchGetImage',
            'ecr:GetAuthorizationToken',
            'ecr:BatchCheckLayerAvailability'
          ],
          resources = ['*'],
        )
      ]
    )

    cognito_role = iam.Role(self, 'PrivateECRIdentityPoolRole',
      assumed_by = iam.FederatedPrincipal(
        federated = 'cognito-identity.amazonaws.com',
        conditions = {
          'StringEquals': {
            'cognito-identity.amazonaws.com:aud': ecr_auth_identity.ref
          },
          'ForAnyValue:StringLike': {
            'cognito-identity.amazonaws.com:amr': 'authenticated'
          }
        },
        assume_role_action = 'sts:AssumeRoleWithWebIdentity'
      )
    )

    cognito_role.add_managed_policy(cognito_policy)

    cognito.CfnIdentityPoolRoleAttachment(self, 'PrivateECRIdentityPoolPolicyAttachment',
      identity_pool_id = ecr_auth_identity.ref,
      roles = {
        'authenticated': cognito_role.role_arn
      }
    )