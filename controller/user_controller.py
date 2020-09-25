from flask import (
    jsonify,
    Blueprint
)

def create_user_endpoints(services, Session):
    user_service = services
    user_bp = Blueprint('user', __name__, url_prefix = '/api/user')

    @user_bp.route('/', methods = ['GET'])
    """
    Args:
        services : service.py 연결
        Session : db 연결
    Return:
        user_list dictionary 형태로 반환
    Authors:
        hj885353@gmail.com(김해준)
    History;
        2020-09-21 (hj885353@gmail.com) : 초기 생성
    """
    def user_info():
        try:
            session = Session()

            user_info = user_service.get_user_info_service(session)

            return jsonify({'user_list' : [ dict(user) for user in user_info ]})

        except Exception as e:
            return jsonify({'ERROR_MSG' : f'{e}' }), 500

        finally:
            # session close, transaction 종료
            session.close()

    return user_bp