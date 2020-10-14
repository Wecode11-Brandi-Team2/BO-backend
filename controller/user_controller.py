from flask import (
    jsonify,
    Blueprint
)
from flask_request_validator import (
    GET,
    validate_params,
    Param
)
from utils import login_required

def create_user_endpoints(services, Session):
    user_service = services
    user_bp = Blueprint('user', __name__, url_prefix = '/api/user')

    @user_bp.route('/', methods = ['GET'], endpoint = 'user_info')
    @login_required(Session)
    @validate_params(
        Param('mber_no', GET, int, required = False),
        Param('mber_ncnm', GET, str, required = False),
        Param('mber_phone', GET, str, required = False),
        Param('mber_email', GET, str, required = False),
        Param('mber_date_from', GET, str, required = False),
        Param('mber_date_to', GET, str, required = False),
        Param('filterLimit', GET, int, required = False),
        Param('page', GET, int, required = False)
    )
    def user_info(*args, **kwargs):
        """
        Args:
            validate_param : validate_params를 통과 한 QueryString
            Session : db 연결
        Return:
            user_list : user에 대한 정보를 담은 list (r'type : list)
            total_user_number : Response로 보낼 데이터의 숫자 (r'type : int)
            page_number : 마지막 page_number (r'tpye : int)
            db_connection_error, 500
        Authors:
            hj885353@gmail.com(김해준)
        History;
            2020-09-21 (hj885353@gmail.com) : 초기 생성
            2020-10-13 (hj885353@gmail.com)
            기존 : QueryString을 사용한 filtering 기능 없음
                controller에서 dict casting 후 return
            변경 : QueryString을 사용한 filtering 기능 추가
                dao에서 dict casting 한 후 그 값을 controller에서 받아서 return
        """
        valid_param = {}

        valid_param['mber_no']        = args[0] # 회원 번호
        valid_param['mber_ncnm']      = args[1] # 회원 로그인 아이디
        valid_param['mber_phone']     = args[2] # 회원 핸드폰 번호
        valid_param['mber_email']     = args[3] # 회원
        valid_param['mber_date_from'] = args[4] # 등록일시 ~부터
        valid_param['mber_date_to']   = args[5] # 등록일시 ~까지
        valid_param['filterLimit']    = args[6] if args[6] else 10 # 페이지네이션 limit
        valid_param['page']           = args[7] if args[7] else 1 # 페이지네이션 offset

        session = Session()

        try:
            if session:
                # dao와 service를 거친 결과 목록 반환
                user_list_result = user_service.get_user_info_service(valid_param, session)
                # tuple -> list로 casting
                user_list, user_count, page_number = user_list_result
                return jsonify({'user' : user_list, 'total_user_number' : user_count, 'page_number' : page_number})
            else:
                # db connection error
                return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500

        except Exception as e:
            return jsonify({'ERROR_MSG' : f'{e}' }), 500

        finally:
            # db close
            session.close()

    return user_bp