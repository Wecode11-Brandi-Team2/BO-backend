from flask import (
    jsonify,
    Blueprint
)

def create_user_endpoints(services):
    user_service = services
    user_bp = Blueprint('user', __name__, url_prefix = '/user')

    @user_bp.route('/', methods = ['GET'])
    def user_info():
        user_info = user_service.get_user_info_service()

        return user_info
    return user_bp