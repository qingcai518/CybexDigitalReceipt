from playhouse.pool import PooledMySQLDatabase
import redis

# DB
db = PooledMySQLDatabase(
    'digital_receipt',
    max_connections=100,
    stale_timeout=500,
    **{'charset': 'utf8', 'use_unicode': True, 'host': 'localhost', 'user': 'root', 'password': 'BCTech_8888'}
)

# Block chain
# NODE_RPC_URL = 'https://hangzhou.51nebula.com/'
# WALLET_PWD = '123456'
# NODE_RPC = 'wss://hangzhou.51nebula.com/'

# main net.
NODE_RPC_URL = 'https://tokyo-01.cybex.io/'
WALLET_PWD = '123456'
NODE_RPC = 'wss://tokyo-01.cybex.io/'

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
