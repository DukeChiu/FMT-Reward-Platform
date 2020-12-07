from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from application.configration import app_config
from flask_cors import *
import redis
import logging
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = app_config.SQLALCHEMY_DATABASE_URI
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = App_config.SQLALCHEMY_TRACK_MODIFICATIONS
db = SQLAlchemy(app)
CORS(app, supports_credentials=True)
redis_pool = redis.ConnectionPool(host=app_config.host, port=app_config.port, db=app_config.db_code, password=app_config.pwd)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=app_config.root_path + app_config.log_path)
logger = logging.getLogger(__name__)
