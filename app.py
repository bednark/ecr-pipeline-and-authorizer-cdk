#!/usr/bin/env python3
import os
import aws_cdk as cdk
from create_cognito_ecr_auth import CreateCognitoECRAuth

app = cdk.App()
CreateCognitoECRAuth(app, 'CreateCognitoECRAuthStack')
app.synth()
