#!/usr/bin/env python3

from aws_cdk import core

from serverless_api_authorizer.serverless_api_authorizer_stack import ServerlessApiAuthorizerStack


app = core.App()
ServerlessApiAuthorizerStack(app, "serverless-api-authorizer")

app.synth()
