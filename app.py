from flask          import Flask
from flask_cors     import CORS

from sqlalchemy     import create_engine

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
    db_engine = create_engine(
        app.config['DB_URL'], encoding='utf-8', max_overflow=0)

    # CORS 설정
    CORS(app, resources={r'*': {'origins': '*'}})

    # Persistence layer
    user_dao = UserDao(db_engine)

    # Business layer
    user_service = UserService(user_dao)

    # Presentation layer
    app.register_blueprint(create_user_endpoints(user_service))

    return app