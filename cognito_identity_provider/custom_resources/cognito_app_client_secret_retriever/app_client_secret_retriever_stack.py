from aws_cdk import aws_cloudformation as cfn
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as _logs
from aws_cdk import core


class CognitoAppClientSecretRetrieverStack(core.Construct):
    def __init__(self, scope: core.Construct, id: str, ** kwargs) -> None:
        super().__init__(scope, id)

        # Read Lambda Function Code):
        # Read Lambda Code
        try:
            with open("cognito_identity_provider/custom_resources/cognito_app_client_secret_retriever/lambda_src/index.py",
                      encoding="utf-8",
                      mode="r") as f:
                cognito_app_client_secret_retriever_fn_code = f.read()
        except OSError:
            print("Unable to read Lambda Function Code")
            raise

        # Create IAM Permission Statements that are required by the Lambda

        roleStmt1 = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=["*"],
            actions=["cognito-idp:DescribeUserPoolClient"]
        )
        roleStmt1.sid = "AllowLambdaToDescribeCognitoUserPool"

        roleStmt2 = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=["*"],
            actions=["secretsmanager:CreateSecret",
                     "secretsmanager:TagResource",
                     "secretsmanager:UpdateSecret",
                     "secretsmanager:DeleteSecret"]
        )
        roleStmt2.sid = "AllowLambdaToAddSecrets"

        cognito_app_client_secret_retriever_fn = _lambda.SingletonFunction(
            self,
            "Singleton",
            uuid="mystique30-4ee1-11e8-9c2d-fa7ae01bbebc",
            code=_lambda.InlineCode(
                cognito_app_client_secret_retriever_fn_code),
            handler="index.lambda_handler",
            timeout=core.Duration.seconds(10),
            runtime=_lambda.Runtime.PYTHON_3_7,
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": "INFO",
                "APP_ENV": "Production"
            }
        )

        cognito_app_client_secret_retriever_fn.add_to_role_policy(roleStmt1)
        cognito_app_client_secret_retriever_fn.add_to_role_policy(roleStmt2)

        # Create Custom Loggroup
        cognito_app_client_secret_retriever_fn_lg = _logs.LogGroup(
            self,
            "cognitoAppClientSecretRetriever",
            log_group_name=f"/aws/lambda/{cognito_app_client_secret_retriever_fn.function_name}",
            retention=_logs.RetentionDays.ONE_WEEK,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        user_pool_secrets_creator = cfn.CustomResource(
            self, "Resource",
            provider=cfn.CustomResourceProvider.lambda_(
                cognito_app_client_secret_retriever_fn
            ),
            properties=kwargs,
        )

        self.response = user_pool_secrets_creator.get_att(
            "user_pool_secrets_arn").to_string()
