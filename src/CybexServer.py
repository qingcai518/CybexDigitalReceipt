from flask import Flask
from flask_jwt_extended import JWTManager
from common.Utility import *
from api import CybexAPI, JCTSample

app = Flask(__name__)
app.register_blueprint(CybexAPI.app)
app.register_blueprint(JCTSample.app)

app.config['JSON_AS_ASCII'] = False
app.config["JSON_SORT_KEYS"] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_AUTH_HEADER_PREFIX'] = 'JWT'

jwt = JWTManager(app)
log = Logger("Server")
cache.init_app(app, config=cache_conf)


@app.route('/')
def hello():
    return "Cybex interface for Digital Receipt"


if __name__ == '__main__':
    app.debug = True
    chain_id = get_chain_id()
    if chain_id is None or chain_id == "":
        log.critical("fail to get chain id.")
    else:
        app.run(host='0.0.0.0', port=8081)



