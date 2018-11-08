import json
import time
import hmac
import hashlib
import requests

api_key = 'be4dd2ef02bf6c7205da170e89b99e96'
api_secret = 'e06791211692c0df9e79a90e0fe7cbf5'
memo = 'jctbot'


## 获取签名.
def create_sha256_signature(message):
    key_bytes = bytes(api_secret, 'latin-1')
    data_bytes = bytes(message, 'latin-1')

    signature = hmac.new(key_bytes, data_bytes, hashlib.sha256).hexdigest()
    return signature


## 当前时间milisec.
def current_time():
    return str(round(time.time() * 1000))


## 获取access token.
def get_access_token():
    url = "https://openapi.bitmart.com/v2/authentication"
    message = api_key + ':' + api_secret + ':' + memo

    signature = create_sha256_signature(message)

    data = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": signature
    }
    response = requests.post(url, data=data)
    token = response.json().get('access_token')
    return token


## 设置request headers.
def get_headers():
    time = current_time()
    token = get_access_token()

    authorization = "Bearer {0}".format(token)

    headers = {
        "X-BM-TIMESTAMP": time,
        "X-BM-AUTHORIZATION": authorization
    }
    return headers


## 用户资产.
def walletBalance():
    url = "https://openapi.bitmart.com/v2/wallet"
    headers = get_headers()
    response = requests.get(url, headers=headers)
    print(response.text)


## 挂单.
def placeOrder(amount, price, side, symbol):
    print("==== Place Order ====")
    url = "https://openapi.bitmart.com/v2/orders"

    # 获取access token.
    message = "amount={0}&price={1}&side={2}&symbol={3}".format(amount, price, side, symbol)
    signature = create_sha256_signature(message)

    headers = get_headers()
    headers["X-BM-SIGNATURE"] = signature
    headers["Content-Type"] = "application/json"

    data = {
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "side": side
    }
    json_data = json.dumps(data)
    response = requests.post(url=url, data=json_data, headers=headers)
    print(response.text)

    ###
    # response:
    # error: {"message": xxxxMSG}
    # success: {"entrust_id": xxxID}
    ###

    return response.text


## 订单列表.
def listOrders(symbol, status, offset, limit):
    print("==== List Orders ====")
    url = "https://openapi.bitmart.com/v2/orders?symbol={0}&status={1}&offset={2}&limit={3}".format(symbol, status, offset, limit)
    print(url)
    headers = get_headers()
    response = requests.get(url=url, headers=headers)
    print(response.text)


## 取消订单.
def cancelOrder(order_id):
    print("==== Cancel Order ====")
    url = "https://openapi.bitmart.com/v2/orders/{0}".format(order_id)

    message = "entrust_id={0}".format(order_id)
    signature = create_sha256_signature(message=message)

    headers = get_headers()
    headers["X-BM-SIGNATURE"] = signature

    response = requests.delete(url=url, headers=headers)
    print(response.text)


listOrders(symbol="JCT_ETH", status=3, offset=0, limit=100)
