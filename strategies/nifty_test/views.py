from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import http.client
import json


# Create your views here.
def index(request):
    conn = http.client.HTTPSConnection('www.alphavantage.co')
    conn.request("GET", "/query?function=TIME_SERIES_INTRADAY&symbol=NIFTY&interval=1min&apikey=60MM3J3ZP4VBFHJK")
    resp = conn.getresponse()
    if (resp.status != 200):
        return JsonResponse({"Error":"Could not establish connection to alphavantage"})
    resp_obj = json.loads(resp.read().decode('utf-8'))
    return JsonResponse({"Time Series (1min)":resp_obj['Time Series (1min)']})
