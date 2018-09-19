from flask import request, Blueprint
from common.Utility import *
from datetime import datetime, timedelta

app = Blueprint('admin_api', __name__)


@app.route('/v1/associate', methods=['POST'])
def associate():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    print(data)
    name = data.get('name')
    password = data.get('password')

    print(name)
    print(password)

    if name is None or password is None:
        return error_handler("have no user name or password", 400)
    result = check_account(name, password)
    return result


@app.route('/v1/signup', methods=['POST'])
def signup():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    name = data.get("name")
    password = data.get("password")

    if name is None or password is None:
        return error_handler("have no user name or password", 400)

    result = create_account(name, password)
    return result


@app.route('/v1/balance', methods=['GET'])
def account():
    try:
        name = request.args.get("name")
        symbol = request.args.get("symbol")
        if name is None or symbol is None:
            return error_handler("have no user or symbol", 400)

        result = get_balance(name, symbol)
        return response(result)
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        return error_handler(msg, 400)


## 获取指定名单的所有人的指定资产.
@app.route('/v1/balances', methods=['POST'])
def balances():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    names = data.get("names")
    symbol = data.get("symbol")

    if names is None or len(names)==0 or symbol is None:
        return error_handler("param is not correct", 400)

    result = {}
    for name in names:
        balance = get_balance(name, symbol)
        if balance is None:
            continue
        result[name] = balance.amount
    return response(result)


## 获取指定账号的主流资产.
@app.route('/v1/main_balance', methods=['GET'])
def main_balance():
    try:
        name = request.args.get("name")
        if name is None:
            return error_handler("have no user", 400)

        symbols = ["CYB", "JADE.ETH", "JADE.BTC", "JADE.USDT", "JADE.JCT"]

        result = {}
        for symbol in symbols:
            balance = get_balance(name, symbol)
            if balance is None:
                continue
            result[balance.symbol] = balance.amount
        return response(result)
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        return error_handler(msg, 400)



@app.route('/v1/pairs', methods=['GET'])
def pairs():
    result = get_pairs()
    if result is None:
        return error_handler("fail to get assets pairs", 400)

    return response(result)


@app.route('/v1/ticker', methods=['POST'])
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

    data = get_ticker(from_asset, to_asset)

    result = data.get("result")
    if result is None:
        return error_handler("have no pair", 400)

    return response(result)


@app.route('/v1/market', methods=['POST'])
def market():
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

    data = get_market_history(from_id, to_id, time_type, start, end)
    result = data.get("result")
    if result is None:
        return error_handler("have no market history", 400)
    return response(result)


@app.route('/v1/receipt/add', methods=['POST'])
def add_receipt():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    receipt_at = data.get("receipt_at")
    tel = data.get("tel")
    total_price = data.get("total_price")
    adjust_price = data.get("adjust_price")
    items = data.get("items")

    if receipt_at is None or tel is None or total_price is None or adjust_price is None:
        return error_handler("have no param", 400)

    # 计算hash值.
    # TODO.

    # 登陆到区块链.
    # TODO.

    # 登陆发票信息.
    result = create_receipt(receipt_at, tel, total_price, adjust_price, items)
    if result is None:
        return error_handler("fail to create receipt", 400)

    return response(result)
