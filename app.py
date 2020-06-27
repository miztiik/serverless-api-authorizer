#!/usr/bin/env python3

from aws_cdk import core

from cognito_identity_provider.cognito_identity_provider_stack import CognitoIdentityProviderStack
from premium_api.premium_api_stack import PremiumApiStack
from api_consumers.api_consumers_stack import ApiConsumersStack

app = core.App()


# Cognito Identity Store Stack
cognito_identity_provider = CognitoIdentityProviderStack(
    app,
    "cognito-identity-provider",
    cognito_domain_name="miztiikon",
    description="Cognito Identity Store Stack"
)

# The Premium Content Provider API
premium_content_provider = PremiumApiStack(
    app,
    "premium-content-provider",
    unicorn_user_pool_arn=cognito_identity_provider.unicorn_user_pool.user_pool_arn,
    unicorn_user_pool_res_srv_identifier=cognito_identity_provider.unicorn_user_pool_res_srv_identifier,
    unicorn_read_scope=cognito_identity_provider.unicorn_read_scope,
    unicorn_write_scope=cognito_identity_provider.unicorn_write_scope,
    description="The Premium Content Provider API"
)

# Content Consumers Stack to Access Premium Content
content_consumers = ApiConsumersStack(
    app,
    "content-consumers-stack",
    unicorn_user_pool_secrets_arn=cognito_identity_provider.unicorn_user_pool_secrets_arn,
    premium_content_api_url=premium_content_provider.premium_content_api_url,
    description="Content Consumers Stack to Access Premium Content"
)


# Stack Level Tagging
core.Tag.add(app, key="Owner",
             value=app.node.try_get_context('owner'))
core.Tag.add(app, key="OwnerProfile",
             value=app.node.try_get_context('github_profile'))
core.Tag.add(app, key="GithubRepo",
             value=app.node.try_get_context('github_repo_url'))
core.Tag.add(app, key="Udemy",
             value=app.node.try_get_context('udemy_profile'))
core.Tag.add(app, key="SkillShare",
             value=app.node.try_get_context('skill_profile'))
core.Tag.add(app, key="AboutMe",
             value=app.node.try_get_context('about_me'))

app.synth()
