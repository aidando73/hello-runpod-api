# NOTE: This file is automatically pulled from GitHub and used within this launch template:
# https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#LaunchTemplateDetails:launchTemplateId=lt-031648d4e4611879f


ALERT_THRESHOLD = 8

GPU_TYPES = [
    "NVIDIA H100 80GB HBM3",
]

DATA_CENTERS = [
    "US-KS-2",
]

url = "https://api.runpod.io/graphql"

import requests
import os
import json
import boto3
import time
import datetime

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:838892012396:RunpodWatcherTopic"

sns = boto3.client('sns', region_name='us-east-1')

def get_availability(gpu_type, data_center):
  start_time = time.time()
  print(f"[{datetime.datetime.now()}] Starting API call for {gpu_type} in {data_center}")
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
  end_time = time.time()
  duration = end_time - start_time
  print(f"[{datetime.datetime.now()}] API call completed in {duration:.2f} seconds")
  return body['data']['gpuTypes'][0]['lowestPrice']['maxUnreservedGpuCount']


if __name__ == "__main__":
  while True:
    cycle_start = time.time()
    print(f"[{datetime.datetime.now()}] Starting new check cycle")
    for gpu_type in GPU_TYPES:
      for data_center in DATA_CENTERS:
        print(f"[{datetime.datetime.now()}] Checking for {gpu_type} in {data_center}")
        availability = get_availability(gpu_type, data_center)
        print(f"[{datetime.datetime.now()}] Availability: {availability}")
        if availability >= ALERT_THRESHOLD:
          print(f"[{datetime.datetime.now()}] Alert: {gpu_type} in {data_center} has {availability} GPUs available")
          sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=f"Alert: {gpu_type} in {data_center} has {availability} GPUs available",
            Subject=f"Alert: {gpu_type} in {data_center} has {availability} GPUs available"
          )
          time.sleep(10)
    cycle_end = time.time()
    cycle_duration = cycle_end - cycle_start
    print(f"[{datetime.datetime.now()}] Cycle completed in {cycle_duration:.2f} seconds")
    
    # Only sleep if the cycle took less than 2 seconds (to maintain ~2 second frequency)
    sleep_time = max(0, 2 - cycle_duration)
    if sleep_time > 0:
        print(f"[{datetime.datetime.now()}] Sleeping for {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
    else:
        print(f"[{datetime.datetime.now()}] Cycle took longer than 2 seconds, no sleep needed")
