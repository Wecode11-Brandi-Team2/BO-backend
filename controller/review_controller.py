from flask import (
    jsonify,
    Blueprint,
    request,
    g
)
from flask_request_validator import (
    GET,
    PATH,
    JSON,
    validate_params,
    Param
)
from sqlalchemy import exc
from utils import login_required

def create_review_endpoints(services, Session):
    review_service = services
    review_bp = Blueprint('review', __name__, url_prefix = '/api/review')

    @review_bp.route('/', methods = ['GET'], endpoint = 'get_review_list')
    @login_required(Session)
    @validate_params(
        Param('selectValue', GET, str, required = False),
        Param('REVIEW_TEXT', GET, str, required = False),
        Param('PRODUCT_INQRY_NO', GET, int, required = False),
        Param('MEMBER_NAME', GET, str, required = False),
        Param('registStartDate', GET, str, required = False),
        Param('registEndDate', GET, str, required = False),
        Param('updateStartDate', GET, str, required = False),
        Param('updateEndDate', GET, str, required = False),
        Param('NEW_REGIST', GET, str, required = False),
        Param('NEW_EDIT', GET, str, required = False),
        Param('filterLimit', GET, int, required = False),
        Param('limit', GET, int, required = False),
        Param('offset', GET, int, required = False)
    )
    def get_review_list(*args, **kwargs):
        valid_param = {}

        valid_param['selectValue']      = args[0] # 검색 입력값
        valid_param['REVIEW_TEXT']      = args[1] # 글 내용
        valid_param['PRODUCT_INQRY_NO'] = args[2] # 글 번호
        valid_param['MEMBER_NAME']      = args[3] # 셀러명
        valid_param['registStartDate']  = args[4] # 등록일 시작
        valid_param['registEndDate']    = args[5] # 등록일 끝
        valid_param['updateStartDate']  = args[6] # 수정일 시작
        valid_param['updateEndDate']    = args[7] # 수정일 끝
        valid_param['NEW_REGIST']       = args[8] # 등록일시 최신순
        valid_param['NEW_EDIT']         = args[9] # 수정일시 최신순
        valid_param['filterLimit']      = args[10] # 10개씩 보기
        valid_param['limit']            = args[11] if args[11] else 10 # pagination limit
        valid_param['offset']           = args[12] if args[12] else 0 # pagination offset

        try:
            # db connection
            session = Session()
            if session:
                # dao와 service를 거친 결과 목록 반환
                review_list_result = review_service.get_review_list(valid_param, session)
                # tuple -> list로 casting
                review_list, review_count = review_list_result
                return jsonify({'review_list' : review_list, 'review_count' : review_count})
            else:
                # db connection error
                return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500

        except Exception as e:
            return jsonify({'message': f'{e}'}), 500

        finally:
            # db close
            session.close()


    return review_bp