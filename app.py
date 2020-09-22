from flask          import Flask
from flask_cors     import CORS

from sqlalchemy          import create_engine
from sqlalchemy.pool     import QueuePool
from sqlalchemy.orm import sessionmaker

from model          import UserDao
from service        import UserService
from controller     import create_user_endpoints


def create_app(test_config = None):
    app = Flask(__name__)
    app.debug = True

    if test_config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.update(test_config)

    # DB 연결
    database = create_engine(app.config['DB_URL'], encoding = 'utf-8', poolclass = QueuePool)

    # database와 연동 된 session maker 생성, connection 필요시마다 session instance 생성
    Session = sessionmaker(bind = database)

    # CORS 설정
    CORS(app, resources={r'*': {'origins': '*'}})

    # Persistence layer
    user_dao = UserDao()

    # Business layer
    user_service = UserService(user_dao)

    # Presentation layer
    app.register_blueprint(create_user_endpoints(user_service, Session))

    return app