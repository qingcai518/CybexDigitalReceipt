from flask import request, Blueprint, jsonify, make_response
import json
import websocket
import requests
from bitshares.account import Account

app = Blueprint('jct_api', __name__)

node_rpc_url = 'https://tokyo-01.cybex.io/'


def response(result):
    return make_response(jsonify(result))


def error_handler(msg, code=400):
    return make_response(jsonify({"msg": msg})), code


# 最新価格を取得する.
@app.route('/v1/sample/ticker', methods=['POST'])
def ticker():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    from_asset = data.get("from")
    to_asset = data.get("to")
    if from_asset is None or to_asset is None:
        return error_handler("have no from/to assets", 400)

    try:
        param = {"jsonrpc": "2.0", "method": "get_ticker", "params": [from_asset, to_asset], "id": 1}
        r = requests.post(url=node_rpc_url, data=json.dumps(param), timeout=30)

        if r.status_code != 200:
            raise Exception("fail to request rpc node.")

        data = json.loads(r.text)
        result = data.get("result")
        if result is None:
            return error_handler("have no pair", 400)
        return response(result)
    except Exception as e:
        print(e)
        return error_handler(e, 400)


# chart用データを取得する
@app.route('/v1/sample/market', methods=['POST'])
def sample_market():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    from_symbol = data.get("from")
    to_symbol = data.get("to")
    time_type = data.get("time_type")
    start = data.get("start")
    end = data.get("end")

    if from_symbol is None or to_symbol is None or time_type is None or start is None or end is None:
        return error_handler("have no param", 400)

    # get asset id.
    assets = lookup_assets([from_symbol, to_symbol])
    if assets is None or len(assets) != 2:
        return error_handler("fail to get assets", 400)

    from_asset = assets[0]
    to_asset = assets[1]

    from_id = from_asset.get("id")
    to_id = to_asset.get("id")

    if from_id is None or to_id is None:
        return error_handler("fail to get asset's id", 400)

    try:
        ws = websocket.WebSocket()
        # ws.connect(NODE_RPC)
        ws.connect("wss://tokyo-01.cybex.io/")

        # 使用之前要先登陆和注册.
        login_param = {"id": 1, "method": "call", "params": [1, "login", ["",""]]}
        register_param = {"id": 2, "method": "call", "params": [1, "history", []]}
        # 获取K线信息的参数.
        param = {"id": 5, "method": "call", "params": [2, "get_market_history", [from_id, to_id, time_type, start, end]]}

        print(json.dumps(param))

        ws.send(json.dumps(login_param))
        ws.recv()
        ws.send(json.dumps(register_param))
        ws.recv()
        ws.send(json.dumps(param))
        received = ws.recv()

        data = json.loads(received)
        result = data.get("result")
        if result is None:
            return error_handler("have no market history", 400)
        return response(result)
    except Exception as e:
        return error_handler(e, 400)


@app.route('/v1/sample/balance', methods=['GET'])
def sample_balance():
    try:
        name = request.args.get("name")
        symbol = request.args.get("symbol")
        if name is None or symbol is None:
            return error_handler("have no user or symbol", 400)

        result = get_balance(name, symbol)
        if result is None:
            return error_handler("can not get balance", 400)

        return response(result)
    except Exception as e:
        return error_handler(e, 400)


def lookup_assets(symbols):
    try:
        params = {"jsonrpc": "2.0", "method": "lookup_asset_symbols", "params": [symbols], "id": 1}
        r = requests.post(url=node_rpc_url, data=json.dumps(params), timeout=30)

        if r.status_code != 200:
            raise Exception("fail to get assets' info")

        return json.loads(r.text).get("result")
    except Exception as e:
        print(e)
        return None


def get_user(user_id):
    try:
        params = {"jsonrpc": "2.0", "method": "get_account_by_name", "params": [user_id], "id": 1}
        r = requests.post(url=node_rpc_url, data=json.dumps(params), timeout=30)

        if r.status_code != 200:
            raise Exception("fail to get user info")

        return json.loads(r.text).get("result")
    except Exception as e:
        print(e)
        return None


def get_balance(name, symbol):
    try:
        user = get_user(name)
        uid = user.get("id")
        if uid is None:
            raise Exception("can not found user: {0}".format(name))

        params = {"jsonrpc": "2.0", "method": "get_account_balances", "params": [uid, [symbol]], "id": 1}
        print(params)

        r = requests.post(url=node_rpc_url, data=json.dumps(params), timeout=30)
        data = r.text
        print("data = {0}".format(data))

        if r.status_code != 200:
            raise Exception("fail to get assets info")

        return json.loads(r.text).get("result")
    except Exception as e:
        print(e)
        return None
