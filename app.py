from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker


from model import OrderDao
from service import OrderService
from controller import create_order_endpoints
from config import DB_URL


def create_app(test_config=None):
    app = Flask(__name__)
    app.debug = True

    if test_config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.update(test_config)

    # QueuePool로 DB 연결 설정
    db_engin = create_engine(app.config['DB_URL'], encoding ='utf-8', pool_size=1000, max_overflow=100, poolclass = QueuePool)

    # database engin와 연동된 session maker 생성, connection 필요시마다 session instance 생성
    Session = sessionmaker(bind = db_engin)

    # CORS 설정
    CORS(app, resources={r'*': {'origins': '*'}})

    # Persistence layer
    order_dao = OrderDao()

    # Business layer
    order_service = OrderService(order_dao)

    # Presentation layer
    app.register_blueprint(create_order_endpoints(order_service, Session))

    return app

