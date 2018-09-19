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

log = Logger("Cybex")
cache = Cache()
blockchain = ""
manager = "1.2.2679"
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

        result = instance.create_account(
            account_name=name,
            registrar=manager,
            referrer=manager,
            referrer_percent=50,
            password=password,
            storekeys=False
        )

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
        msg = e.args[len(e.args) - 1]
        return error_handler(msg)


##
def get_balance(name, symbol):
    try:
        account = Account(name)
        balance = account.balance(symbol)
        return balance
    except Exception as e:
        # msg = e.args[len(e.args) - 1]
        # log.error(msg)
        print(e)
        return None


def get_pairs():
    try:
        r = requests.get(url_paris)
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            raise Exception("fail to get assets pairs")

    except Exception as e:
        msg = e.args[len(e.args) -1]
        log.error(msg)
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
        r = requests.post(url=NODE_RPC_URL, data=json.dumps(param), timeout=30)

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
        ws.connect(NODE_RPC)

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
        r = requests.post(url=NODE_RPC_URL, data=json.dumps(params), timeout=30)

        if r.status_code != 200:
            raise Exception("fail to get assets' info")

        print("===============")
        print(r.text)

        return json.loads(r.text).get("result")
    except Exception as e:
        msg = e.args[len(e.args) - 1]
        log.error("fail to get assets {0}".format(msg))


# database access.
def create_receipt(receipt_at, tel, total_price, adjust_price, items):
    print("1111111")
    item_ids = []
    try:
        with db.transaction():
            log.debug("插入receipt信息")
            receipt = Receipt.create(
                receipt_at=receipt_at,
                tel=tel,
                total_price=total_price,
                adjust_price=adjust_price
            )

            if receipt is None:
                return None

            for item in items:
                item_info = Item.create(
                    receipt_id=receipt.id,
                    name=item.name,
                    price=item.price
                )
                if item_info is None:
                    continue
                item_ids.append(item_info.id)
            db.commit()

            result = {
                "receipt_id": receipt.id,
                "items": item_ids
            }
            return result
    except Exception as e:
        db.rollback()
        msg = e.args[len(e.args) - 1]
        log.error("fail to create receipt".format(msg))
        return None
