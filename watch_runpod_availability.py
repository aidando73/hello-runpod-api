# NOTE: This file is automatically pulled from GitHub and used within this launch template:
# https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#LaunchTemplateDetails:launchTemplateId=lt-031648d4e4611879f


ALERT_THRESHOLD = 8

GPU_TYPES = [
    "NVIDIA H100 80GB HBM3",
    "NVIDIA H100 NVL",
    "NVIDIA H200",
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

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:838892012396:RunpodWatcherTopic"

sns = boto3.client('sns', region_name='us-east-1')

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
    for gpu_type in GPU_TYPES:
      for data_center in DATA_CENTERS:
        print(f"Checking for {gpu_type} in {data_center}")
        availability = get_availability(gpu_type, data_center)
        print(f"Availability: {availability}")
        if availability >= ALERT_THRESHOLD:
          print(f"Alert: {gpu_type} in {data_center} has {availability} GPUs available")
          sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=f"Alert: {gpu_type} in {data_center} has {availability} GPUs available",
            Subject=f"Alert: {gpu_type} in {data_center} has {availability} GPUs available"
          )
          time.sleep(10)
    time.sleep(2)
