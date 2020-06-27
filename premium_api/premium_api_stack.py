from aws_cdk import aws_apigateway as _apigw
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as _logs
from aws_cdk import core

import os


class PremiumApiStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        unicorn_user_pool_arn,
        unicorn_user_pool_res_srv_identifier,
        unicorn_read_scope,
        unicorn_write_scope,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create Serverless Event Processor using Lambda):
        # Read Lambda Code
        try:
            with open("premium_api/lambda_src/premium_content.py", mode="r") as f:
                premium_content_fn_code = f.read()
        except OSError:
            print("Unable to read Lambda Function Code")
            raise

        premium_content_fn = _lambda.Function(
            self,
            "premiumContentFunction",
            function_name="premium_function",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="index.lambda_handler",
            code=_lambda.InlineCode(
                premium_content_fn_code),
            timeout=core.Duration.seconds(3),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": "INFO",
                "Environment": "Production"
            }
        )

        # Create Custom Loggroup
        # /aws/lambda/function-name
        premium_content_fn_lg = _logs.LogGroup(
            self,
            "premiumContentFnLoggroup",
            log_group_name=f"/aws/lambda/{premium_content_fn.function_name}",
            retention=_logs.RetentionDays.ONE_WEEK,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # Add API GW front end for the Lambda
        walled_garden_api_stage_options = _apigw.StageOptions(
            stage_name="prod",
            throttling_rate_limit=10,
            throttling_burst_limit=100,
            logging_level=_apigw.MethodLoggingLevel.INFO
        )

        # Create API Gateway
        api_01 = _apigw.LambdaRestApi(
            self,
            "walledGardenApi",
            rest_api_name="walled-garden-api",
            deploy_options=walled_garden_api_stage_options,
            endpoint_types=[
                _apigw.EndpointType.REGIONAL
            ],
            handler=premium_content_fn,
            proxy=False
        )

        # Add the wall to the garden - API Authorizer
        api_01_authorizer = _apigw.CfnAuthorizer(
            self,
            "walledGardenApiAuthorizer",
            name="walledGardenSentry",
            rest_api_id=api_01.rest_api_id,
            type="COGNITO_USER_POOLS",
            provider_arns=[unicorn_user_pool_arn],
            authorizer_result_ttl_in_seconds=15,
            identity_source="method.request.header.Authorization"
        )

        get_content = api_01.root.add_resource("home")
        # premium_content = get_content.add_resource("{premium}")
        premium_content = get_content.add_resource("premium")
        premium_content_method_get = premium_content.add_method(
            "GET",
            authorization_type=_apigw.AuthorizationType.COGNITO,
            authorization_scopes=[
                f"{unicorn_user_pool_res_srv_identifier}/{unicorn_read_scope}"
            ]
        )

        premium_content_method_get.node.find_child("Resource").add_property_override(
            "AuthorizerId", api_01_authorizer.ref)
        # Add POST method
        premium_content_method_post = premium_content.add_method(
            "POST",
            authorization_type=_apigw.AuthorizationType.COGNITO,
            authorization_scopes=[
                f"{unicorn_user_pool_res_srv_identifier}/{unicorn_write_scope}"
            ]
        )
        premium_content_method_post.node.find_child("Resource").add_property_override(
            "AuthorizerId", api_01_authorizer.ref)

        # Export API Endpoint URL
        self.premium_content_api_url = premium_content.url

        # Outputs
        output_1 = core.CfnOutput(self,
                                  "PremiumApiUrl",
                                  value=f"{premium_content.url}",
                                  description="Use a browser to access this url"
                                  )
