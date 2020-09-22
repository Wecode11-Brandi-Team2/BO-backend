from flask import (
    jsonify,
    Blueprint
)

def create_user_endpoints(services, Session):
    user_service = services
    user_bp = Blueprint('user', __name__, url_prefix = '/user')

    @user_bp.route('/', methods = ['GET'])
    def user_info():
        try:
            session = Session()

            user_info = user_service.get_user_info_service(session)

            return user_info

        except Exception as e:
            return jsonify({'ERROR_MSG' : f'{e}' }), 500

        finally:
            # session close, transaction 종료
            session.close()

    return user_bp