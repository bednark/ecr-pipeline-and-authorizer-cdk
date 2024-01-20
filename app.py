#!/usr/bin/env python3
import os
import aws_cdk as cdk
from create_cognito_ecr_auth import CreateCognitoECRAuth
from cognito_auth_api import CognitoAuthAPI

app = cdk.App()
CreateCognitoECRAuth(app, 'CreateCognitoECRAuthStack')
CognitoAuthAPI(app, 'CognitoAuthAPIStack')
app.synth()
