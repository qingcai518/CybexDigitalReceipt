from log.Logger import Logger
import requests
import json, time
from flask import jsonify, make_response
from bitsharesbase.cybexchain import cybex_config
from bitshares import BitShares
from bitshares.account import Account
from db.DBModel import *
from flask_caching import Cache
import websocket
from cybex import Asset, Market

log = Logger("Cybex")
cache = Cache()
blockchain = ""
url_paris = "https://app.cybex.io/lab/exchange/asset"


def response(result):
    return make_response(jsonify(result))


def error_handler(msg, code=400):
    return make_response(jsonify({"msg": msg})), code


def post_request_until_success(post_data):
    while True:
        try:
            r = requests.post(url=NODE_RPC_URL, data=json.dumps(post_data), timeout=30)

            if r.status_code == 200:
                return json.loads(r.text)['result']
            else:
                raise Exception("fail to request rpc node.")
        except Exception as e:
            log.error(e)
            time.sleep(1)


def get_chain_id():
    try:
        param = {"jsonrpc": "2.0", "method": "get_chain_properties", "params": [], "id": 1}
        result = post_request_until_success(param)
        blockchain = result.get("chain_id")
        cybex_config(node_rpc_endpoint=NODE_RPC, chain_id=blockchain)
        return blockchain
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        log.error("fail to get chain id {0}".format(msg))
    return None


def create_account(name, password):
    try:
        instance = BitShares(node=NODE_RPC, **{'prefix': 'cyb'})
        instance.wallet.unlock(WALLET_PWD)

        print("account name = {0}".format(name))
        print("registrar = {0}".format(ADMIN_USER_ID))
        print("password = {0}".format(password))

        result = instance.create_account(
            account_name=name,
            registrar=ADMIN_USER_ID,
            referrer=ADMIN_USER_ID,
            referrer_percent=50,
            password=password,
            storekeys=False
        )

        print("result = {0}".format(result))

        # add to user table.
        try:
            data = result["operations"][0][1]
            owner_key = data["owner"]["key_auths"][0][0]
            active_key = data["active"]["key_auths"][0][0]
            memo_key = data["options"]["memo_key"]
        except Exception:
            print("can not get keys")

        User.create(**{
            "name": name,
            "password": fn.md5(password),
            "owner_pub_key": owner_key,
            "active_pub_key": active_key,
            "memo_pub_key": memo_key
        })
        return response(result)
    except Exception as e:
        print(e)
        msg = e.args[len(e.args) - 1]
        return error_handler(msg, 400)


##
def get_balance(name, symbol):
    try:
        account = Account(name)
        balance = account.balance(symbol)
        return balance
    except Exception as e:
        log.error(e)
        return None


##
def get_balances(name):
    try:
        account = Account(name)
        balances = account.balances
        for balance in balances:
            print(balance)
        return balances
    except Exception as e:
        log.error(e)
        return None


def get_pairs():
    try:
        r = requests.get(url_paris)
        if r.status_code == 200:
            result = json.loads(r.text)
            try:
                result.get("JADE.ETH").append("JADE.JCT")
            except Exception as e:
                print(e)

            return result
        else:
            raise Exception("fail to get assets pairs")

    except Exception as e:
        log.error(e)
        return None


def check_account(name, password):
    from bitsharesbase.account import PasswordKey, PublicKey
    prefix = 'CYB'

    active_key = PasswordKey(name, password, role="active")
    owner_key = PasswordKey(name, password, role="owner")
    memo_key = PasswordKey(name, password, role="memo")

    active_pubkey = active_key.get_public()
    owner_pubkey = owner_key.get_public_key()
    memo_pubkey = memo_key.get_public_key()

    active = format(active_pubkey, prefix)
    owner = format(owner_pubkey, prefix)
    memo = format(memo_pubkey, prefix)

    print("active key = {0}".format(active))
    print("owner key = {0}".format(owner))
    print("memo key = {0}".format(memo))

    # 在区块链上根据public key来寻找这名用户.
    try:
        instance = BitShares(node=NODE_RPC, **{'prefix': 'cyb'})
        instance.wallet.unlock(WALLET_PWD)

        account = instance.wallet.getAccountFromPublicKey(owner)
        print(account)

        activekey = instance.wallet.getActiveKeyForAccount(account)
        memokey = instance.wallet.getMemoKeyForAccount(account)
        print(activekey)
        print(memokey)
        if account is None:
            raise Exception("not exists user.")

        result = {
            "active_key": activekey,
            "owner_key": owner,
            "memo_key": memokey
        }

        print(result)

        User.create(**{
            "name": name,
            "password": fn.md5(password),
            "owner_pub_key": owner,
            "active_pub_key": active,
            "memo_pub_key": memo
        })

        return response(result)
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        return error_handler(msg, 400)


def get_ticker(from_asset, to_asset):
    try:
        param = {"jsonrpc": "2.0", "method": "get_ticker", "params": [from_asset, to_asset], "id": 1}
        # r = requests.post(url=NODE_RPC_URL, data=json.dumps(param), timeout=30)
        r = requests.post(url="https://tokyo-01.cybex.io/", data=json.dumps(param), timeout=30)

        if r.status_code != 200:
            raise Exception("fail to request rpc node.")

        return json.loads(r.text)
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        log.error("fail to get chain id {0}".format(msg))


def get_trade_history(from_asset, to_asset, time):
    try:
        param = {"jsonrpc": "2.0", "method": "get_trade_history", "params": [from_asset, to_asset, time, time, 1], "id": 1}
        r = requests.post(url=NODE_RPC_URL, data=json.dumps(param), timeout=30)

        if r.status_code != 200:
            raise Exception("fail to get trade history by sequence")

        return json.loads(r.text)
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        log.error("fail to get chain id {0}".format(msg))


def get_market_history(from_id, to_id, time_type, start, end):
    try:
        ws = websocket.WebSocket()
        # ws.connect(NODE_RPC)
        ws.connect("wss://tokyo-01.cybex.io/")  # dummy. 只能从主网获取k线信息.

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
        result = ws.recv()

        return json.loads(result)
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        log.error("fail to get market history {0}".format(msg))


def lookup_assets(symbols):
    try:
        params = {"jsonrpc": "2.0", "method": "lookup_asset_symbols", "params": [symbols], "id": 1}
        # r = requests.post(url=NODE_RPC_URL, data=json.dumps(params), timeout=30)
        r = requests.post(url="https://tokyo-01.cybex.io/", data=json.dumps(params), timeout=30)   # 需要连接所有节点才能取到k线用信息.

        if r.status_code != 200:
            raise Exception("fail to get assets' info")

        print("===============")
        print(r.text)

        return json.loads(r.text).get("result")
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        log.error("fail to get assets {0}".format(msg))


def get_user(user_id):
    try:
        params = {"jsonrpc": "2.0", "method": "get_account_by_name", "params": [user_id], "id": 1}
        r = requests.post(url=NODE_RPC_URL, data=json.dumps(params), timeout=30)

        if r.status_code != 200:
            raise Exception("fail to get user info")

        return json.loads(r.text).get("result")
    except Exception as e:
        log.error(e)


def get_user_pub_key(uid):
    try:
        user = get_user(uid)
        if user is None:
            raise Exception("can not found admin user.")

        key_auths = user.get("active").get("key_auths")
        if key_auths is None or len(key_auths) == 0 or len(key_auths[0]) == 0:
            raise Exception("can not found active infos from key auths")

        return key_auths[0][0]
    except Exception as e:
        log.error(e)
        return None


def do_transfer(from_uid, to_uid, asset, amount, lock_time, memo):
    log.info("==== do transfer ==== from:{0} to:{1} {2}:{3}".format(from_uid, to_uid, asset, amount))
    try:
        user_pub_key = get_user_pub_key(to_uid)

        net = BitShares(node=NODE_RPC, **{'prefix': 'cyb'})
        net.wallet.unlock(WALLET_PWD)
        account = Account(from_uid, bitshares_instance=net)

        # 锁定期.
        extensions = []
        if lock_time > 0:
            extensions.append(1)
            extensions.append({"vesting_period": lock_time, "public_key": user_pub_key})

        if len(extensions) > 0:
            params = []
            params.append(extensions)

            dic = {'prefix': 'cyb', 'extensions': params}
            result = net.transfer(to_uid, amount, asset, memo, account=account, **dic)
        else:
            result = net.transfer(to_uid, amount, asset, memo, account=account)

        log.info(result)
        return result
    except Exception as e:
        log.error(e)
        return None


def order(from_symbol, to_symbol, from_count, to_count, uid):
    try:
        instance = BitShares(node=NODE_RPC, **{'prefix': 'cyb'})
        instance.wallet.unlock(WALLET_PWD)

        from_asset = Asset(from_symbol)
        to_asset = Asset(to_symbol)
        market = Market(base=from_asset, quote=to_asset, cybex_instance=instance)

        buy_result = market.buy(from_count, to_count, 3600, killfill=False, account=uid)
        sell_result = market.sell(from_count, to_count, 3600, killfill=False, account=ADMIN_USER)

        print(buy_result)
        print(sell_result)

    except Exception as e:
        print(e)
        return None


def get_chain_properties():
    try:
        param = {"jsonrpc": "2.0", "method": "get_chain_properties", "params": [], "id": 1}
        r = requests.post(url=NODE_RPC_URL, data=json.dumps(param), timeout=30)

        if r.status_code != 200:
            raise Exception("fail to get trade history by sequence")

        return json.loads(r.text)
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        log.error("fail to get chain id {0}".format(msg))


# database access.
def do_login(name, password):
    try:
        user = User.select(
            User.name,
            User.active_pub_key,
            User.memo_pub_key,
            User.owner_pub_key,
            User.created_at,
            User.update_at,
        ).where(
            User.name == name,
            User.password == fn.MD5(password)
        ).get()

        if user is None:
            raise Exception("fail to login")

        result = {"name": user.name,
                  "owner_pub_key": user.owner_pub_key,
                  "active_pub_key": user.active_pub_key,
                  "memo_pub_key": user.memo_pub_key,
                  "created_at": user.created_at,
                  "update_at": user.update_at
                  }
        return result
    except Exception as e:
        log.error(e)
        return None


def create_receipt(image_path, hash, receipt_at, tel, total_price, adjust_price, items):
    item_infos = []
    try:
        with db.transaction():
            log.debug("插入receipt信息")

            params = {
                "image_path": image_path,
                "hash": hash
            }
            if receipt_at is not None:
                params["receipt_at"] = receipt_at
            if tel is not None:
                params["tel"] = tel
            if total_price is not None:
                params["total_price"] = total_price
            if adjust_price is not None:
                params["adjust_price"] = adjust_price

            data_source = [
                params
            ]
            receipt_id = Receipt.insert_many(data_source).execute()
            if receipt_id is None:
                return None

            if items is not None and len(items) > 0:
                for item in items:
                    itemName = item["name"]
                    itemPrice = item["price"]

                    if itemName is None or itemPrice is None:
                        continue

                    item_info = Item.create(
                        receipt_id=receipt_id,
                        name=itemName,
                        price=itemPrice
                    )
                    if item_info is None:
                        continue
                    item_infos.append({"id": item_info.id, "name": itemName, "price": itemPrice})

            db.commit()
            result = {
                "receipt_id": receipt_id,
                "items": item_infos
            }
            return result
    except Exception as e:
        db.rollback()
        log.error(e)
        return None
