from playhouse.pool import PooledMySQLDatabase
import redis

#DB
db = PooledMySQLDatabase(
    'recika',
    # 'digital_receipt',
    max_connections=100,
    stale_timeout=500,
    **{'charset': 'utf8', 'use_unicode': True, 'host': '52.197.86.134', 'user': 'root', 'password': 'Longhash_8888'}
    # **{'charset': 'utf8', 'use_unicode': True, 'host': 'localhost', 'user': 'root', 'password': 'Longhash_8888'}
)

# Block chain
NODE_RPC_URL = 'https://hangzhou.51nebula.com/'
WALLET_PWD = 'longhash'
NODE_RPC = 'wss://hangzhou.51nebula.com/'    # 用测试链无法取到chart用的信息.

# main net.
# NODE_RPC_URL = 'https://tokyo-01.cybex.io/'
# WALLET_PWD = '123456'
# NODE_RPC = 'ws://18.136.17.169:8090/'    // 在新的aws上面不能用wss, 只能用ws的地址.
# NODE_RPC = 'wss://tokyo-01.cybex.io/'

# Redis api cache.
cache_conf = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': '6379',
    'CACHE_KEY_PREFIX': 'dr_'
}

# Redis for store.
rds = redis.Redis(host='localhost', port=6379)

## base user and asset infos.
ADMIN_USER = "zhuanzhi518"
ADMIN_USER_ID = "1.2.4432"
BASE_ASSET = "CYB"
BASE_REWARD = 0.1
