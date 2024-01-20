import os, boto3, botocore.exceptions, base64
from botocore.config import Config

boto_config = Config(region_name = os.environ['REGION'])
idp_client = boto3.client('cognito-idp', config=boto_config)
identity_client = boto3.client('cognito-identity', config=boto_config)

def lambda_handler(event, context):

  try:
    idp_response = idp_client.initiate_auth(
      ClientId=os.environ['CLIENT_ID'],
      AuthFlow=('USER_PASSWORD_AUTH'),
      AuthParameters={
        'USERNAME': event['username'],
        'PASSWORD': event['password']
      }
    )

    token_id = idp_response['AuthenticationResult']['IdToken']

    get_id = identity_client.get_id(
      IdentityPoolId=os.environ['IDENTITY_ID'],
      Logins={
        os.environ['IDP_POOL']: token_id
      }
    )

    temp_identity_id = get_id['IdentityId']

    get_credentials = identity_client.get_credentials_for_identity(
      IdentityId=temp_identity_id,
      Logins={
        os.environ['IDP_POOL']: token_id
      }
    )

    access_key = get_credentials['Credentials']['AccessKeyId']
    secret_key = get_credentials['Credentials']['SecretKey']
    session_token = get_credentials['Credentials']['SessionToken']

    ecr_client = boto3.client('ecr',
      aws_access_key_id=access_key,
      aws_secret_access_key=secret_key,
      aws_session_token=session_token
    )

    get_ecr_auth = ecr_client.get_authorization_token()
    ecr_user, ecr_passwd = base64.b64decode(get_ecr_auth['authorizationData'][0]['authorizationToken']).decode().split(':')
    expires_at = str(get_ecr_auth['authorizationData'][0]['expiresAt'])
    ecr_endpoint = get_ecr_auth['authorizationData'][0]['proxyEndpoint'].replace('https://', '')

    return {
      "statusCode": 200,
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        'username': ecr_user,
        'password': ecr_passwd,
        'expires_at': expires_at,
        'ecr_endpoint': ecr_endpoint
      }
    }
  except (idp_client.exceptions.NotAuthorizedException,
    idp_client.exceptions.UserNotFoundException,
    idp_client.exceptions.ForbiddenException):
    return {
      "statusCode": 401,
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        'error_msg': 'Not Authorized'
      }
    }
  except Exception as e:
    print(e)
    return {
      "statusCode": 500,
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        'error_msg': 'Internal server error'
      }
    }