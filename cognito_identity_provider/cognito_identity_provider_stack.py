from aws_cdk import core
from aws_cdk import aws_cognito as _cognito
import os

from cognito_identity_provider.custom_resources.cognito_app_client_secret_retriever.app_client_secret_retriever_stack import CognitoAppClientSecretRetrieverStack


class global_args:
    """"
    Helper to define global statics
    """

    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = "serverless-api-authorizer"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_06_23"
    MIZTIIK_SUPPORT_EMAIL = ["mystique@example.com", ]


class CognitoIdentityProviderStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, cognito_domain_name: str, ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here):

        svc_name = self.node.try_get_context("service_name")

        url_name = core.CfnParameter(
            self,
            id="cognitoDomainName",
            description="Enter the name the domain you want to use",
            type="String",
            default="mystique"
        )

        # Create an Identity Pool
        self.unicorn_user_pool = _cognito.UserPool(
            self,
            "unicornUserPool",
            user_pool_name="Miztiik-Unicorn-App-User-Pool",
            # sign_in_aliases={"username": True,"email": True}
            sign_in_aliases=_cognito.SignInAliases(username=True, email=True),
            standard_attributes={
                "email": {
                    "required": True,
                    "mutable": False
                },
                "fullname": {
                    "required": False,
                    "mutable": True
                }
            },
            auto_verify=_cognito.AutoVerifiedAttrs(email=True)
        )

        # OAuth Scopes
        self.unicorn_user_pool_res_srv_identifier = f"premium_api"
        self.unicorn_read_scope = f"read"
        self.unicorn_write_scope = f"write"

        unicorn_users_auth_domain = _cognito.UserPoolDomain(
            self,
            "userPoolDomain",
            user_pool=self.unicorn_user_pool,
            cognito_domain=_cognito.CognitoDomainOptions(
                domain_prefix=f"{cognito_domain_name}"
            )
        )

        self.unicorn_user_pool.user_pool_arn

        user_pool_res_srv = _cognito.CfnUserPoolResourceServer(
            self,
            "ResourceServer",
            # Having URL format is recommended
            # identifier=f"{premium_content.url}",
            identifier=f"{self.unicorn_user_pool_res_srv_identifier}",
            name=f"premium-api-authorizer",
            user_pool_id=self.unicorn_user_pool.user_pool_id,
            scopes=[
                {
                    "scopeName":  f"{self.unicorn_read_scope}",
                    "scopeDescription": "Get Premium Api Content"
                },
                {
                    "scopeName":  f"{self.unicorn_write_scope}",
                    "scopeDescription": "Put Premium Api Content"
                }
            ]
        )

        user_pool_client = _cognito.UserPoolClient(
            self,
            "AppClient",
            user_pool=self.unicorn_user_pool,
            user_pool_client_name="premium_app_users",
            generate_secret=True,
            # We'll allow both Flows, Implicit and Authorization Code, and decide in the app which to use.
            auth_flows=_cognito.AuthFlow(
                admin_user_password=False,
                custom=True,
                refresh_token=True,
                user_password=False,
                user_srp=True
            ),
            prevent_user_existence_errors=True,
            o_auth=_cognito.OAuthSettings(
                flows=_cognito.OAuthFlows(
                    authorization_code_grant=False, implicit_code_grant=False, client_credentials=True),
                scopes=[
                    # _cognito.OAuthScope.EMAIL,
                    # _cognito.OAuthScope.OPENID,
                    # _cognito.OAuthScope.COGNITO_ADMIN,
                    # _cognito.OAuthScope.PROFILE,
                    # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_cognito/OAuthScope.html#aws_cdk.aws_cognito.OAuthScope
                    _cognito.OAuthScope.custom(
                        f"{self.unicorn_user_pool_res_srv_identifier}/{self.unicorn_read_scope}"),
                    _cognito.OAuthScope.custom(
                        f"{self.unicorn_user_pool_res_srv_identifier}/{self.unicorn_write_scope}")
                ]
            )
        )

        # Add dependency so that ResourceServer is deployed before App Client
        user_pool_client.node.add_dependency(user_pool_res_srv)

        # Retrieve Cognito App Client Secret and Add to Secrets Manager
        app_secrets = CognitoAppClientSecretRetrieverStack(
            self,
            "appClientSecrets",
            user_pool_id=self.unicorn_user_pool.user_pool_id,
            user_pool_client_id=user_pool_client.user_pool_client_id,
            user_pool_oauth2_endpoint=f"https://{unicorn_users_auth_domain.domain_name}.auth.{core.Aws.REGION}.amazoncognito.com/oauth2/token",
            unicorn_user_pool_res_srv_identifier=f"{self.unicorn_user_pool_res_srv_identifier}",
            unicorn_read_scope=f"{self.unicorn_read_scope}",
            unicorn_write_scope=f"{self.unicorn_write_scope}"
        )

        # Export Value
        self.unicorn_user_pool_secrets_arn = app_secrets.response

        ###########################################
        ################# OUTPUTS #################
        ###########################################

        output_0 = core.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{global_args.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page."
        )
        # https://AUTH_DOMAIN/oauth2/token
        output_1 = core.CfnOutput(
            self,
            "UnicornIdentityAuthDomain",
            value=f"https://{unicorn_users_auth_domain.domain_name}.auth.{core.Aws.REGION}.amazoncognito.com/oauth2/token",
            description="Authenticate Against this endpoint"
        )

        output_2 = core.CfnOutput(
            self,
            "AppPoolSecretsArn",
            value=f"{app_secrets.response}",
            description="AppPoolSecretsArn"
        )
