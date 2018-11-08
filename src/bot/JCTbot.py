import json
import time
import hmac
import hashlib
import requests

# api_key = 'b4eec5db92db4530a6758f47cd78e9b4'
# api_secret = 'e851bba3ca8ad898930c5edcbb80d41a'
# memo = 'JCT'
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


## 仓位.
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
    headers = get_headers()
    response = requests.get(url=url, headers=headers)
    print(response.text)


## 取消订单.
def cancelOrder(order_id):
    print("==== Cancel Order ====")
    url = "https://openapi.bitmart.com/v2/orders/1223181"
    headers = get_headers()
    message = "entrust_id={0}".format(order_id)
    signature = create_sha256_signature(message=message)
    headers["X-BM-SIGNATURE"] = signature

    response = requests.delete(url=url, headers=headers)
    print(response.text)


# 调用注文api.
result = placeOrder(amount=1, price=0.00135, side="buy", symbol="JCT_ETH")
print("result = {0}".format(result))

# 调用注文列表.
# listOrders(symbol="BMX_ETH", status=0, offset=0, limit=100)

# 调用取消注文api.
# cancelOrder(order_id=order_id)

# 获取钱包列表.
# walletBalance()
