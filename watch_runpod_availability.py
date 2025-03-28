
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
              "id": "NVIDIA H100 80GB HBM3"
          },
          "lowestPriceInput": {
              "gpuCount": 1,
              "minDisk": 0,
              "minMemoryInGb": 8,
              "minVcpuCount": 2,
              "secureCloud": True,
              "compliance": None,
              "dataCenterId": "US-KS-2",
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
        print(f"Checking {gpu_type} in {data_center}")
        print(get_availability(gpu_type, data_center))
    time.sleep(10)
