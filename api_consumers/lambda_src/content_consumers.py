# -*- coding: utf-8 -*-
"""
.. module: premium_content
    :Actions: Validate requests with Cognito
    :copyright: (c) 2020 Mystique.,
.. moduleauthor:: Mystique
.. contactauthor:: miztiik@github issues
"""

import boto3
import json
import logging
import os
from botocore.vendored import requests


__author__ = "Mystique"
__email__ = "miztiik@github"
__version__ = "0.0.1"
__status__ = "production"


class global_args:
    """ Global statics """
    OWNER = "Mystique"
    ENVIRONMENT = "production"
    MODULE_NAME = "premium_content"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    USER_POOL_SECRETS_ARN = os.getenv("USER_POOL_SECRETS_ARN")
    PREMIUM_CONTENT_API_URL = os.getenv("PREMIUM_CONTENT_API_URL")


def set_logging(lv=global_args.LOG_LEVEL):
    """ Helper to enable logging """
    logging.basicConfig(level=lv)
    logger = logging.getLogger()
    logger.setLevel(lv)
    return logger


# Initial some defaults in global context to reduce lambda start time, when re-using container
logger = set_logging()

_sec_client = boto3.client("secretsmanager")


def _cog_auth_token(api_path):
    _t = ""
    try:
        resp = _sec_client.get_secret_value(
            SecretId=global_args.USER_POOL_SECRETS_ARN
        )
        _d = json.loads(resp["SecretString"])

        oauth2_url = _d["user_pool_oauth2_endpoint"]
        client_id = _d["user_pool_client_id"]
        client_secret = _d["app_client_secret"]
        grant_type = "client_credentials"

        resp = requests.post(
            oauth2_url,
            auth=(client_id, client_secret),
            data={
                "grant_type": grant_type,
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": f"{_d['unicorn_user_pool_res_srv_identifier']}/{api_path}"
            }
        )
        logger.debug(resp.json())
        _t = resp.json()["access_token"]
        logger.debug(_t)
    except Exception as e:
        logger.error(f"{str(e)}")
    return _t


def get_content(e):
    data = f""
    _t = ""
    _m_verb = "GET"
    api_path = e["requestContext"]["resourcePath"]
    logger.debug(f"api_path:{api_path}")

    if api_path == "/content/authorized-read" or api_path == "/content/authorized-write":
        _t = _cog_auth_token(api_path.split("-")[1])

    if api_path == "/content/authorized-write":
        _m_verb = "POST"

    try:
        resp = requests.request(
            _m_verb,
            global_args.PREMIUM_CONTENT_API_URL,
            headers={"Authorization": _t}
        )
        logger.debug(f"ResData:{resp.text}")
        data = json.loads(resp.text)
        if "message" in data:
            data = data["message"]
    except Exception as e:
        logger.error(f"{str(e)}")

    if not data:
        data = "Something Obviously went wrong, Let me check"
    logger.debug(data)
    return data


def lambda_handler(event, context):
    logger.debug(f"received_event:{event}")
    try:
        data = ""
        data = get_content(event)
    except Exception as e:
        logger.error(f"{str(e)}")

    if not data:
        data = "Something Obviously went wrong, Let me check"
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": data
            }
        )
    }
