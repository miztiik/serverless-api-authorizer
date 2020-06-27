from aws_cdk import aws_apigateway as _apigw
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as _logs
from aws_cdk import aws_iam as _iam
from aws_cdk import core

import os


class ApiConsumersStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        unicorn_user_pool_secrets_arn,
        premium_content_api_url,
        ** kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create Serverless Event Processor using Lambda):
        # Read Lambda Code
        try:
            with open("api_consumers/lambda_src/content_consumers.py", mode="r") as f:
                content_consumers_fn_code = f.read()
        except OSError:
            print("Unable to read Lambda Function Code")
            raise

        content_consumers_fn = _lambda.Function(
            self,
            "contentConsumersFn",
            function_name="content_consumers",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="index.lambda_handler",
            code=_lambda.InlineCode(
                content_consumers_fn_code),
            timeout=core.Duration.seconds(3),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": "DEBUG",
                "Environment": "Production",
                "USER_POOL_SECRETS_ARN": unicorn_user_pool_secrets_arn,
                "PREMIUM_CONTENT_API_URL": premium_content_api_url,
            }
        )

        roleStmt1 = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=[unicorn_user_pool_secrets_arn],
            actions=[
                "secretsmanager:GetSecretValue"
            ]
        )
        roleStmt1.sid = "AllowLambdaToReadSecrets"

        content_consumers_fn.add_to_role_policy(roleStmt1)

        # Create Custom Loggroup
        # /aws/lambda/function-name
        content_consumers_fn_lg = _logs.LogGroup(
            self,
            "contentConsumersFnLoggroup",
            log_group_name=f"/aws/lambda/{content_consumers_fn.function_name}",
            retention=_logs.RetentionDays.ONE_WEEK,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # Add API GW front end for the Lambda
        miztiik_world_api_stage_options = _apigw.StageOptions(
            stage_name="miztiik",
            throttling_rate_limit=10,
            throttling_burst_limit=100,
            logging_level=_apigw.MethodLoggingLevel.INFO
        )

        # Create API Gateway
        api_01 = _apigw.LambdaRestApi(
            self,
            "miztiikWorld",
            rest_api_name="miztiik-world-api",
            deploy_options=miztiik_world_api_stage_options,
            endpoint_types=[
                _apigw.EndpointType.REGIONAL
            ],
            handler=content_consumers_fn,
            proxy=False
        )

        get_content = api_01.root.add_resource("content")

        # GET Unauthorized Request
        get_unauthorized_request = get_content.add_resource(
            "unauthorized-read")
        get_unauthorized_request_method = get_unauthorized_request.add_method(
            "GET")
        # GET Authorized Request
        get_authorized_request = get_content.add_resource("authorized-read")
        get_authorized_request_method = get_authorized_request.add_method(
            "GET")
        # PUT Authorized Request
        post_authorized_request = get_content.add_resource(
            "authorized-write")
        post_authorized_request_method = post_authorized_request.add_method(
            "GET")

        output_1 = core.CfnOutput(self,
                                  "UnauthorizedUrl",
                                  value=f"{get_unauthorized_request.url}",
                                  description="Use a browser to access this url"
                                  )
        output_2 = core.CfnOutput(self,
                                  "GetAuthorizedUrl",
                                  value=f"{get_authorized_request.url}",
                                  description="Use a browser to access this url"
                                  )
        output_2 = core.CfnOutput(self,
                                  "PostAuthorizedUrl",
                                  value=f"{post_authorized_request.url}",
                                  description="Use a browser to access this url"
                                  )
