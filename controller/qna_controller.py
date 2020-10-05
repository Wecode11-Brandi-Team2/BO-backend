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

def create_qna_endpoints(services, Session):
    qna_service = services
    qna_bp = Blueprint('qna', __name__, url_prefix = '/api/qna')

    @qna_bp.route('/', methods = ['GET'], endpoint = 'get_qna_list')
    @login_required(Session)
    @validate_params(
        Param('product_name', GET, str, required = False),
        Param('product_inqry_no', GET, int, required = False),
        Param('md_ko_name', GET, str, required = False),
        Param('order_no', GET, int, required = False),
        Param('inquiry_type', GET, str, required = False),
        Param('regist_date_from', GET, str, required = False),
        Param('regist_date_to', GET, str, required = False),
        Param('offset', GET, int, required = False),
        Param('limit', GET, int, required = False)
    )
    def get_qna_list(*args, **kwargs):
        """
        Q&A list를 보여주는 함수
        valildate_params를 통과한 QueryString을 인자로 받는다.

        Args:
            product_name : 상품명
            product_inqry_no : 글 번호
            md_ko_name : 셀러 한글명
            order_no : 회원번호
            inquiry_type : 문의 유형
            regist_date_from : 등록일 ~부터
            regist_date_to : 등록일 ~까지
            offset : pagination offset
            limit : pagination limit
        Returns:
            qna_list : 조건을 충족하는 Q&A 목록 (r'type : dict)
            qna_count : 전체 갯수와 조건을 만족하는 Q&A 갯수 (r'type : dict)
            DB_CONNECTION_ERROR, 500
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-05 (hj885353@gmail.com) : 초기 생성
        """
        valid_param = {}

        valid_param['product_name']     = args[0] # 상품명
        valid_param['product_inqry_no'] = args[1] # 글 번호
        valid_param['md_ko_name']       = args[2] # 셀러 한글명
        valid_param['order_no']         = args[3] # 회원 번호
        valid_param['inquiry_type']     = args[4] # 문의 유형
        valid_param['regist_date_from'] = args[5] # 등록일 ~부터
        valid_param['regist_date_to']   = args[6] # 등록일 ~까지
        valid_param['limit']            = args[8] if args[8] else 20 # pagination limit
        valid_param['offset']           = args[7] if args[7] else 0 # pagination offset

        # decorator로부터 받아온 seller info를 가진 g 객체
        seller_info = g.seller_info

        try:
            # db connection
            session = Session()
            if session:
                # dao와 service를 거친 결과 목록 반환
                qna_list_result = qna_service.get_qna_list(valid_param, seller_info, session)
                # tuple -> list로 casting
                qna_list, qna_count = qna_list_result
                return jsonify({'qna_list' : qna_list, 'qna_count' : qna_count})
            else:
                # db connection error
                return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500

        except Exception as e:
            return jsonify({'message': f'{e}'}), 500

        finally:
            # db close
            session.close()

    return qna_bp