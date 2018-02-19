from regender import PatternGenderSwapper
import cStringIO
import logging
import boto3
import os
import json
import string
import random
import jsonschema
import jsonschema.exceptions
import hashlib

logger = logging.getLogger()
logger.setLevel("INFO")

ID_SIZE=20
INPUT_PREFIX="texts"

# Event looks like this:
# {
#     "body": "That's what she said.",
#     "headers": null,
#     "httpMethod": "POST",
#     "isBase64Encoded": false,
#     "path": "/regender",
#     "pathParameters": null,
#     "queryStringParameters": null,
#     "requestContext": {
#         "accountId": "string",
#         "apiId": "string",
#         "httpMethod": "POST",
#         "identity": {
#             "accessKey": "string",
#             "accountId": "string",
#             "apiKey": "string",
#             "apiKeyId": "string",
#             "caller": "string",
#             "cognitoAuthenticationProvider": null,
#             "cognitoAuthenticationType": null,
#             "cognitoIdentityId": null,
#             "cognitoIdentityPoolId": null,
#             "sourceIp": "test-invoke-source-ip",
#             "user": "string",
#             "userAgent": "Apache-HttpClient/4.5.x (Java/1.8.0_144)",
#             "userArn": "string"
#         },
#         "path": "/regender",
#         "requestId": "test-invoke-request",
#         "resourceId": "string",
#         "resourcePath": "/regender",
#         "stage": "string"
#     },
#     "resource": "/regender",
#     "stageVariables": null
# }

def regender_start(event, context):
    response = {
        "statusCode": 500,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({"message": "Internal server error"})
    }

    try:
        input_bucket = os.environ["inputBucket"]

        input_body = event["body"]

        id = generate_id(ID_SIZE)
        key = os.path.join(INPUT_PREFIX, id)

        s3 = boto3.client("s3")
        put_response = s3.put_object(Body=input_body, Bucket=input_bucket, Key=key, ContentType="text/plain")

        response.update({"statusCode": 200, "body": json.dumps({"id": id})})
    except Exception as e:
        logger.exception(e)
        response.update({"statusCode": 500, "body": e.message})
    return response

# Event looks like this:
#
# {
#   "Records": [
#     {
#       "eventVersion": "2.0",
#       "eventName": "ObjectCreated:Put",
#       "eventTime": "YYYY-mm-ddTHH:MM:SS.000Z",
#       "userIdentity": {
#         "principalId": "string"
#       },
#       "eventSource": "aws:s3",
#       "requestParameters": {
#         "sourceIPAddress": "string"
#       },
#       "s3": {
#         "configurationId": "string",
#         "object": {
#           "eTag": "string",
#           "key": "string",
#           "sequencer": "string",
#           "size": int
#         },
#         "bucket": {
#           "ownerIdentity": {
#             "principalId": "string"
#           },
#           "name": "string",
#           "arn": "string"
#         },
#         "s3SchemaVersion": "1.0"
#       },
#       "responseElements": {
#         "x-amz-id-2": "string",
#         "x-amz-request-id": "string"
#       },
#       "awsRegion": "string"
#     }
#   ]
# }
def regender_go(event, context):
    logger.warning(event)
    logger.warning(context)
    response = {
        "statusCode": 500,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body" : "Internal server error"
    }

    output_bucket = os.environ.get("outputBucket", None)
    if not output_bucket:
        logger.error("Could not get outputBucket environment variable")
        return response

    with open("s3schema.json", "r") as sf:
        schema = json.load(sf)

    try:
        jsonschema.validate(event, schema)

        s3 = boto3.client('s3')
        for record in event["Records"]:
            bucket = record["s3"]["bucket"]["name"]
            key = record["s3"]["object"]["key"]
            etag = record["s3"]["object"]["eTag"]
            get_response = s3.get_object(
                Bucket=bucket,
                IfMatch=etag,
                Key=key
            )
            body_stream = get_response["Body"]
            fp = cStringIO.StringIO(body_stream.read())
            output = cStringIO.StringIO()
            swapper = PatternGenderSwapper()
            for line in swapper.swap_gender(fp):
                output.write(line)
                output.write("\n")

            put_response = s3.put_object(
                Body=output.getvalue(),
                Bucket=output_bucket,
                Key=key
            )

            logger.debug("Saved response with eTag {0}".format(put_response["ETag"]))

        response.update({
            "statusCode": 200,
            "body": "Response has been recorded in s3://{0}/{1}".format(output_bucket, key)
        })
    except jsonschema.exceptions.ValidationError as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(e)
    return response

def regender_status(event, context):
    """
    Get status of a conversion
    :param event:
    :param context:
    :return:
    """
    response = {
        "statusCode": 500,
        "body" : json.dumps({"message": "Not yet implemented"})
    }
    return response

def regender_result(event, context):
    """
    Get result of a conversion
    :param event:
    :param context:
    :return:
    """
    response = {
        "statusCode": 500,
        "body" : json.dumps({"message": "Not yet implemented"})
    }
    return response

def generate_id(size, prefix=None, chars=string.ascii_uppercase + string.digits):
    """
    Generate a random string of characters
    :param size:
    :param prefix:
    :param chars:
    :return:
    """
    return "{0}{1}".format(prefix if prefix else "",''.join(random.choice(chars) for _ in range(size)))

