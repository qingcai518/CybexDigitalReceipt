import json
import time
import requests

memo = 'JCT'
grant_type = 'client_credentials'
client_id = 'b4eec5db92db4530a6758f47cd78e9b4'
client_secret = '188fcaa99b123182b356042f016cda0777eaee3ed576ad962b5fbae8ece4c0a7'

## the way to get client_secret:
# echo -n "api_key:api_secret:memo" | openssl dgst -sha256 -hmac "api_secret"


def get_access_token():
    url = "https://openapi.bitmart.com/v2/authentication"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, data=data)
    token = response.json().get('access_token')
    return token


# place an order.
def placeOrder(token):
    url = "https://openapi.bitmart.com/v2/orders"
    current_milli_time = lambda : int(round(time.time() * 1000))
    print(current_milli_time)
    authorization = "Bearer {0}".format(token)
    headers = {
        "X-BM-TIMESTAMP": current_milli_time,
        "X-BM-AUTHORIZATION": authorization,
        "X-BM-SIGNATURE": "df658d1d61537a842dba5ddb3f69a96f04a87ba4a9b3fba478cece39cb5da57f",
        "Content-Type": "application/json"}
    data = {
        "symbol": "BMX_ETH",
        "amount": 1,
        "price": 1,
        "side": "buy"
    }
    json_data = json.dumps(data)
    response = requests.post(url=url, data=json_data, headers=headers)
    print(response.text)


access_token = get_access_token()
print(access_token)

print("==== begin to send an order.")
placeOrder(access_token)
print("==== end send an order.")

token = get_access_token()
print(token)

print("get token and to send place an order.")
placeOrder(token)
print("finish to send an order.")

