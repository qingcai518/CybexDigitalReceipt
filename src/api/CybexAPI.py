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


@app.route('/v1/login', methods=['POST'])
def login():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    name = data.get("name")
    password = data.get("password")

    if name is None or password is None:
        return error_handler("have no user name or password", 400)

    result = do_login(name, password)
    if result is None:
        return error_handler("fail to login", 400)
    return response(result)


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


## 获取指定账号的主流资产.
@app.route('/v1/main_balance', methods=['GET'])
def main_balance():
    try:
        name = request.args.get("name")
        if name is None:
            return error_handler("have no user", 400)

        symbols = ["CYB", "JADE.ETH", "JADE.BTC", "JADE.USDT", "JADE.JCT", "RCP", "BPT", "DPT"]

        result = []
        for symbol in symbols:
            balance = get_balance(name, symbol)
            print(balance)
            if balance is None:
                continue

            result.append({"symbol": balance.symbol, "amount": balance.amount})
        return response(result)
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        return error_handler(msg, 400)


@app.route('/v1/account_balances', methods=['GET'])
def account_balances():
    try:
        # name = request.args.get("name")
        # if name is None:
        #     return error_handler("have no user", 400)

        result = get_named_account_balances()
        return response(result)
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        return error_handler(msg, 400)


@app.route('/v1/uid', methods=['GET'])
def get_account_id():
    try:
        name = request.args.get("name")
        if name is None:
            return error_handler("have no user", 400)

        user = get_user(name)
        return response(user)
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        return error_handler(msg, 400)


@app.route('/v1/assets', methods=['POST'])
def get_assets():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        params = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    assets = params.get("assets")
    if assets is None or len(assets) == 0:
        return error_handler("have no assets", 400)

    data = lookup_asset_symbols(assets)

    if data is None:
        return error_handler("have no result", 400)

    return response(data)


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


@app.route('/v1/order', methods=['POST'])
def do_order():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    from_symbol = data.get("from_symbol")
    to_symbol = data.get("to_symbol")

    from_count = data.get("from_count")
    to_count = data.get("to_count")

    uid = data.get("user_id")

    if uid is None or from_symbol is None or to_symbol is None or from_count is None or to_count is None:
        return error_handler("param not fill", 400)

    try:
        result = order(from_symbol=from_symbol, to_symbol=to_symbol, from_count=from_count, to_count=to_count, uid=uid)
        return response(result)
    except Exception as e:
        return error_handler(e, 400)


@app.route('/v1/broadcast', methods=['POST'])
def do_broadcast():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    tx = data.get("transaction")
    if tx is None:
        return error_handler("fail to get transaction.")

    try:
        result = broadcast(tx)
        return response(result)
    except Exception as e:
        return error_handler(e, 400)


@app.route('/v1/chain', methods=['GET'])
def chain():
    try:
        data = get_dynamic_global_properties()
        result = data.get("result")
        if result is None:
            return error_handler("fail to get result", 400)
        return response(result)
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        return error_handler(msg, 400)


@app.route('/v1/chain_id', methods=['GET'])
def chain_id():
    try:
        chain_id = get_chain_id()
        result = {"chain_id": chain_id}
        return response(result)
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        return error_handler(msg, 400)


@app.route('/v1/transfer', methods=['POST'])
def transfer():
    request.environ["CONTENT_TYPE"] = "application/json"
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    from_name = data.get("from_name")
    to_name = data.get("to_name")
    private_key = data.get("private_key")
    amount = data.get("amount")
    symbol = data.get("symbol")
    memo = data.get("memo")

    print("from name = {0}".format(from_name))
    print("to name = {0}".format(to_name))
    print("private key = {0}".format(private_key))
    print("amount = {0}".format(amount))
    print("symbol = {0}".format(symbol))
    print("memo = {0}".format(memo))

    try:
        result = ws_transfer(from_name=from_name, to_name=to_name, amount=amount, symbol=symbol, private_key=private_key, memo=memo)
        return response(result)
    except Exception as e:
        return error_handler(e, 400)



