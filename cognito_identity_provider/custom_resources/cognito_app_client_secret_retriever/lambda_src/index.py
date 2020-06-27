# -*- coding: utf-8 -*-

import logging as log
import os
import json
import boto3
import cfnresponse
log.getLogger().setLevel(log.INFO)

_cog_client = boto3.client("cognito-idp")
_sec_client = boto3.client("secretsmanager")


def get_app_client_secret(app_client_id, user_pool_id):
    _sec = ""
    try:
        _pool_info = _cog_client.describe_user_pool_client(
            UserPoolId=user_pool_id,
            ClientId=app_client_id
        )
        _sec = _pool_info.get("UserPoolClient").get("ClientSecret")
    except Exception as e:
        log.error(f"{str(e)}")
    return _sec


def _put_secret(cfn_stack_name, res_id, s):
    try:
        r = _sec_client.create_secret(
            Description="User Pool Secrets",
            Name=f"cognito_{s['user_pool_id']}",
            SecretString=json.dumps(s),
            Tags=[
                {
                    "Key": "custom:cloudformation:stack-name",
                    "Value": cfn_stack_name
                },
                {
                    "Key": "custom:cloudformation:logical-id",
                    "Value": res_id
                },
                {
                    "Key": "custom:cloudformation:created-by",
                    "Value": f"Fn-{os.environ['AWS_LAMBDA_FUNCTION_NAME']}"
                }
            ]
        )
        return r["ARN"]
    except Exception as e:
        log.error(f"{str(e)}")
        raise


def _delete_secret(s):
    try:
        _sec_client.delete_secret(
            SecretId=s,
            ForceDeleteWithoutRecovery=True
        )
    except Exception as e:
        log.error(f"{str(e)}")
        raise


def lambda_handler(event, context):
    log.info(f"event: {event}")
    physical_id = 'TheOnlyCustomResource'

    try:
        # MINE
        sec_arn = ""
        cfn_stack_name = event.get("StackId").split("/")[-2]
        resource_id = event.get("LogicalResourceId")
        user_pool_id = event["ResourceProperties"].get("User_pool_id")
        user_pool_client_id = event["ResourceProperties"].get(
            "User_pool_client_id")

        app_secrets = {
            "app_client_secret": "",
            "user_pool_id": user_pool_id,
            "user_pool_client_id": user_pool_client_id,
            "user_pool_oauth2_endpoint": event["ResourceProperties"].get(
                "User_pool_oauth2_endpoint"),
            "unicorn_user_pool_res_srv_identifier": event["ResourceProperties"].get(
                "Unicorn_user_pool_res_srv_identifier"),
            "unicorn_read_scope": event["ResourceProperties"].get(
                "Unicorn_read_scope"),
            "unicorn_write_scope": event["ResourceProperties"].get(
                "Unicorn_write_scope")
        }
        if event["RequestType"] == "Create" and event["ResourceProperties"].get(
            "FailCreate", False
        ):
            log.info(f"FailCreate")
            raise RuntimeError("Create failure requested")
        if event["RequestType"] == "Create":
            app_secrets["app_client_secret"] = get_app_client_secret(
                user_pool_client_id, user_pool_id)
            sec_arn = _put_secret(cfn_stack_name, resource_id, app_secrets)
        elif event["RequestType"] == "Update":
            app_secrets["app_client_secret"] = get_app_client_secret(
                user_pool_client_id, user_pool_id)
            sec_arn = _put_secret(cfn_stack_name, resource_id, app_secrets)
        elif event["RequestType"] == "Delete":
            _delete_secret(f"cognito_{app_secrets['user_pool_id']}")
        else:
            log.error("FAILED!")
            return cfnresponse.send(event, context, cfnresponse.FAILED, {}, physical_id)

        # MINE
        attributes = {
            "user_pool_secrets_arn": f"{sec_arn}"
        }

        cfnresponse.send(event, context, cfnresponse.SUCCESS,
                         attributes, physical_id)
    except Exception as e:
        log.exception(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, physical_id)
