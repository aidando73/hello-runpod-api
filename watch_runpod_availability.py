# NOTE: This file is automatically pulled from GitHub and used within this launch template:
# https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#LaunchTemplateDetails:launchTemplateId=lt-031648d4e4611879f


ALERT_THRESHOLD = 8

GPU_TYPES = [
    "NVIDIA H100 80GB HBM3",
    "NVIDIA H100 NVL",
    "NVIDIA H100 PCIe",
    "NVIDIA H200",
    "NVIDIA A100-SXM4-80GB",
    "NVIDIA A100 80GB PCIe",
]

DATA_CENTERS = [
    "US-KS-2",
    "CA-MTL-3",
]

url = "https://api.runpod.io/graphql"

import requests
import os
import json
import boto3
from twilio.rest import Client


# SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:838892012396:RunpodWatcherTopic"
# sns = boto3.client('sns', region_name='us-east-1')
# ssm = boto3.client('ssm', region_name='us-east-1')

# account_sid = ssm.get_parameter(
#     Name='/runpod/twilio/account_sid',
#     WithDecryption=True
# )['Parameter']['Value']
# auth_token = ssm.get_parameter(
#     Name='/runpod/twilio/auth_token',
#     WithDecryption=True
# )['Parameter']['Value']

secrets_manager = boto3.client('secretsmanager', region_name='us-east-1')
secret_id = "arn:aws:secretsmanager:us-east-1:838892012396:secret:twillio_credentials-gJGMdi"
secret = json.loads(secrets_manager.get_secret_value(SecretId=secret_id)['SecretString'])
accounts_sid = secret['account_id']
auth_token = secret['auth_token']
phone_number = secret['phone_number']

twilio_client = Client(accounts_sid, auth_token)

def get_availability(gpu_type, data_center):
  query = """
  query SecureGpuTypes($lowestPriceInput: GpuLowestPriceInput, $gpuTypesInput: GpuTypeFilter) {
    gpuTypes(input: $gpuTypesInput) {
      lowestPrice(input: $lowestPriceInput) {
        minimumBidPrice
        uninterruptablePrice
        minVcpu
        minMemory
        stockStatus
        compliance
        maxUnreservedGpuCount
        __typename
      }
      id
      displayName
      memoryInGb
      securePrice
      communityPrice
      oneMonthPrice
      oneWeekPrice
      threeMonthPrice
      sixMonthPrice
      secureSpotPrice
      __typename
    }
  }
  """

  payload = {
      "operationName": "SecureGpuTypes",
      "query": query,
      "variables": {
          "gpuTypesInput": {
              "id": gpu_type
          },
          "lowestPriceInput": {
              "gpuCount": 1,
              "minDisk": 0,
              "minMemoryInGb": 8,
              "minVcpuCount": 2,
              "secureCloud": True,
              "compliance": None,
              "dataCenterId": data_center,
              "globalNetwork": True
          }
      }
  }
  # Make the GraphQL request
  response = requests.post(url, json=payload)
  body = response.json()
  return body['data']['gpuTypes'][0]['lowestPrice']['maxUnreservedGpuCount']


import time

if __name__ == "__main__":
  while True:
    # Print timestamp for logging purposes
    # Set timezone to Australia/Sydney
    from datetime import datetime
    from datetime import timezone, timedelta
    sydney_tz = timezone(timedelta(hours=11))
    current_time = datetime.now(sydney_tz).strftime("%d %b %H:%M:%S")
    print(f"\n[{current_time}]")
    print(f"{'GPU Type':<23} {'DC':<10} {'GPUs':<3}")
    for gpu_type in GPU_TYPES:
      for data_center in DATA_CENTERS:
        availability = get_availability(gpu_type, data_center)
        print(f"{gpu_type:<23} {data_center:<10} {availability:<3}")
        if availability >= ALERT_THRESHOLD:
          print(f"Alert: {gpu_type} in {data_center} has {availability} GPUs available")
          twilio_client.messages.create(
            from_=phone_number,
            to="+61421229074",
            body=f"Alert: {gpu_type} in {data_center} has {availability} GPUs available"
          )
          time.sleep(60 * 5)
    time.sleep(2)
