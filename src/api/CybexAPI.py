from flask import request, Blueprint
from common.Utility import *
import crypt

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


## 获取指定名单的所有资产.
@app.route('/v1/balances', methods=['POST'])
def get_balances():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    names = data.get("names")
    symbols = data.get("symbols")

    if names is None or len(names)==0 or symbols is None or len(symbols) == 0:
        return error_handler("param is not correct", 400)

    result = {}
    for name in names:
        tokens = []
        for symbol in symbols:
            balance = get_balance(name, symbol)
            if balance is None:
                continue
            tokens.append(balance.amount)
        result[name] = tokens
    return response(result)


## 获取指定账号的主流资产.
@app.route('/v1/main_balance', methods=['GET'])
def main_balance():
    try:
        name = request.args.get("name")
        if name is None:
            return error_handler("have no user", 400)

        symbols = ["CYB", "JADE.ETH", "JADE.BTC", "JADE.USDT", "JADE.JCT", "JADE.RCP", "JADE.BPT", "JADE.DPT"]

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

    user_id = data.get("user_id")
    receipt_at = data.get("receipt_at")
    tel = data.get("tel")
    total_price = data.get("total_price")
    adjust_price = data.get("adjust_price")
    image_path = data.get("image_path")
    items = data.get("items")

    # check image path.
    if image_path is None:
        return error_handler("image path を指定してください.")

    # 计算hash值.
    hash = crypt.crypt(json.dumps(data))
    log.info("hash ====> {0}".format(hash))


    # 登陆到区块链.
    # 登陆一笔转账信息.
    transfer_result = do_transfer(ADMIN_USER, user_id, BASE_ASSET, BASE_REWARD, 0, hash)
    if transfer_result is None:
        return error_handler("fail to do transfer")

    # 登陆发票信息.
    results = create_receipt(image_path, hash, receipt_at, tel, total_price, adjust_price, items)
    if results is None:
        return error_handler("fail to create receipt infos.")

    return response(results)


@app.route('/v1/account/fetch', methods=['POST'])
def get_account_id():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    uid = data.get("user_id")
    if uid is None:
        return error_handler("have no user id", 400)

    user = get_user(uid)
    print(user)

    if user is None:
        return error_handler("fail to get user", 400)

    return response(user)
