from flask import Flask
from flask_cors import CORS

from sqlalchemy          import create_engine
from sqlalchemy.pool     import QueuePool
from sqlalchemy.orm      import sessionmaker

from model          import (
    OrderDao,
    UserDao,
    SellerDao,
    ProductDao,
    QnADao,
    ReviewDao,
    CouponDao
)
from service        import (
    OrderService,
    UserService,
    SellerService,
    ProductService,
    QnAService,
    ReviewService,
    CouponService
)
from controller     import (
    create_order_endpoints,
    create_user_endpoints,
    create_seller_endpoints,
    create_product_endpoints,
    create_qna_endpoints,
    create_review_endpoints,
    create_coupon_endpoints
)

import utils

def create_app(test_config = None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.update(test_config)

    # pool size : 1000, max_overflow=100 인 QueuePool로 DB 연결 설정
    database = create_engine(app.config['DB_URL'], encoding ='utf-8', pool_size = 1000, max_overflow = 100, poolclass = QueuePool)

    # database engin와 연동된 session maker 생성, connection 필요시마다 session instance 생성
    Session = sessionmaker(bind = database)

    # CORS 설정
    CORS(app, resources={r'*': {'origins': '*'}})

    # Persistence layer
    order_dao = OrderDao()
    user_dao = UserDao()
    seller_dao = SellerDao()
    product_dao = ProductDao()
    qna_dao = QnADao()
    review_dao = ReviewDao()
    coupon_dao = CouponDao()

    # Business layer
    order_service = OrderService(order_dao)
    user_service = UserService(user_dao)
    seller_service = SellerService(seller_dao)
    product_service = ProductService(product_dao)
    qna_service = QnAService(qna_dao)
    review_service = ReviewService(review_dao)
    coupon_service = CouponService(coupon_dao)

    # Presentation layer
    app.register_blueprint(create_order_endpoints(order_service, Session))
    app.register_blueprint(create_user_endpoints(user_service, Session))
    app.register_blueprint(create_seller_endpoints(seller_service, Session))
    app.register_blueprint(create_product_endpoints(product_service, Session))
    app.register_blueprint(create_qna_endpoints(qna_service, Session))
    app.register_blueprint(create_review_endpoints(review_service, Session))
    app.register_blueprint(create_coupon_endpoints(coupon_service, Session))

    return app