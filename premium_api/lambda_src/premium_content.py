# -*- coding: utf-8 -*-
"""
.. module: content_consumers
    :Actions: Validate requests with Cognito
    :copyright: (c) 2020 Mystique.,
.. moduleauthor:: Mystique
.. contactauthor:: miztiik@github issues
"""

import boto3
import json
import logging
import os


__author__ = "Mystique"
__email__ = "miztiik@github"
__version__ = "0.0.1"
__status__ = "production"


class global_args:
    """ Global statics """
    OWNER = "Mystique"
    ENVIRONMENT = "production"
    MODULE_NAME = "content_consumers"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def set_logging(lv=global_args.LOG_LEVEL):
    """ Helper to enable logging """
    logging.basicConfig(level=lv)
    logger = logging.getLogger()
    logger.setLevel(lv)
    return logger


# Initial some defaults in global context to reduce lambda start time, when re-using container
logger = set_logging(logging.INFO)


def get_premium_content(e):
    data = f"Premium Content: OAuth Scope: Read"
    logger.info(data)
    return data


def post_premium_content(e):
    data = f"Premium Content: OAuth Scope: Write"
    logger.info(data)
    return data


def lambda_handler(event, context):
    logger.info(f"received_event:{event}")
    # event['httpMethod']
    try:
        data = ""
        http_method = event["requestContext"]["httpMethod"]

        logger.info(f"http_method:{http_method}")

        if http_method == "GET":
            data = get_premium_content(event)
        elif http_method == "POST":
            data = post_premium_content(event)
        else:
            data = ValueError(f"Unsupported method: {http_method}")

    except Exception as e:
        logger.error(f"{str(e)}")

    if not data:
        data = "Something Obviously went wrong, Let me check"
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": data
        })
    }
