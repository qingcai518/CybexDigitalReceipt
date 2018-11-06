from flask import request, Blueprint, jsonify, make_response
import websocket
import requests
from log.Logger import Logger
import json, time
from flask import jsonify, make_response
import cybex
from bitsharesbase.cybexchain import cybex_config
from bitshares import BitShares
from bitshares.account import Account
from db.DBModel import *
from flask_caching import Cache
import websocket
from websocket import create_connection
from common.Utility import *

app = Blueprint('jct_test_api', __name__)

node_rpc_url = 'https://hangzhou.51nebula.com/'
wallet_pwd = 'longhash'
cybex_admin = 'zhuanzhi518'


# 最新価格を取得する.
@app.route('/v1/jct/create_asset', methods=['POST'])
def create_asset():
    request.environ['CONTENT_TYPE'] = 'application/json'
    try:
        data = request.get_json()
    except Exception:
        return error_handler("参数形式错误")

    symbol = data.get("symbol")   # 资产符号.
    supply = data.get("supply")   # 资产供给量.
    precision_str = data.get("precision")  # 资产的精度.
    description = data.get("description")  # 详细描述.
    ratio_str = data.get("ratio")  # 手续费比例.

    # 手续费比例, 默认是 1:1 CYB
    ratio = 1
    precision = 6
    try:
        ratio = int(ratio_str)
        precision = int(precision_str)
    except Exception as e:
        print(e)

    core_exchange_ratio = {'CTB': 1, symbol: ratio}

    if symbol is None or supply is None:
        return error_handler("should input symbol and supply")


    try:
        instance = BitShares(node=node_rpc_url, **{'prefix': 'cyb'})
        instance.wallet.unlock(wallet_pwd)

        result = instance.create_asset(
            symbol=symbol,
            precision=precision,
            max_supply=supply,
            core_exchange_ratio=core_exchange_ratio,
            description=description,
            charge_market_fee=True,      # 发行人是否可以后期调整资产的charge_market_fee
            white_list=True,             # 发行人是否可以后期调整资产的white_list
            override_authority=True,     # 发行人是否可以后期调整资产的override_authority
            transfer_restricted=True,    # 发行人是否可以后期调整资产的transfer_restricted
            is_prediction_market=False,  # 预测市场资产，对于普通资产设置为False
            account=cybex_admin   # 创建人.
        )

        print(result)
        return response(result)
    except Exception as e:
        print(e)
        return error_handler(e)