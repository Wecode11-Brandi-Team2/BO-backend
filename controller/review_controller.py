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
        Param('page', GET, int, required = False)
    )
    def get_review_list(*args, **kwargs):
        """
        Review list 반환해주는 함수

        filtering 기능을 사용하기 위해 validate_params를 사용해 Querystring으로 원하는 형태의 값이 들어왔는지 validation 확인 후
        해당 값을 필터링 해서 보내주는 함수

        Args:
            valid_param : validate_params에서 통과 한 QueryString.
            session : db connection 객체
        Returns:
            get_review_result : 글 번호, 셀러명, 상품명, 회원닉네임, 리뷰내용, 등록일시, 수정일시 return (r'type : dict)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-07 (hj885353@gmail.com) : 초기 생성
            2020-10-12 (hj885353@gmail.com) : 페이지네이션 filterLimit, page 사용하여 로직 수정
             - 마지막 페이지 number return 하도록 수정
             - 검색 카테고리가 선택되지 않은 상태에서의 검색 입력값만은 불필요하기 때문에 삭제
            2020-10-13 (hj885353@gmail.com) : pagination querystring 입력되지 않았을 경우를 위한 default값 설정
        """
        valid_param = {}

        valid_param['REVIEW_TEXT']      = args[0] # 글 내용
        valid_param['PRODUCT_INQRY_NO'] = args[1] # 글 번호
        valid_param['MEMBER_NAME']      = args[2] # 셀러명
        valid_param['registStartDate']  = args[3] # 등록일 시작
        valid_param['registEndDate']    = args[4] # 등록일 끝
        valid_param['updateStartDate']  = args[5] # 수정일 시작
        valid_param['updateEndDate']    = args[6] # 수정일 끝
        valid_param['NEW_REGIST']       = args[7] # 등록일시 최신순
        valid_param['NEW_EDIT']         = args[8] # 수정일시 최신순
        valid_param['filterLimit']      = args[9] if args[9] else 10 # 10개씩 보기
        valid_param['page']             = args[10] if args[10] else 0 # page number

        try:
            # db connection
            session = Session()
            if session:
                # dao와 service를 거친 결과 목록 반환
                review_list_result = review_service.get_review_list(valid_param, session)
                # tuple -> list로 casting
                review_list, review_count, page_number = review_list_result
                return jsonify({'review' : review_list, 'total_review_number' : review_count, 'page_number' : page_number})
            else:
                # db connection error
                return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500

        except Exception as e:
            return jsonify({'message': f'{e}'}), 500

        finally:
            # db close
            session.close()

    @review_bp.route('/<int:parameter_review_no>', methods = ['GET'], endpoint = 'review_info')
    @login_required(Session)
    @validate_params(
        Param('parameter_review_no', PATH, int, required = True)
    )
    def review_info(*args, **kwargs):
        """
        리뷰 내용 보기 버튼 눌렀을 때, 모달창에 띄워지는 데이터를 반환해주는 함수

        리뷰 버튼을 눌렀을 때, 해당 리뷰에 대한 내용을 보여주어야 하기 때문에 글 번호를 path_parameter로 받아,
        해당 글에 대한 정보를 반환해주도록 합니다.

        Args:
            review_no : validate_params에서 통과 한 path_parameter.
            session : db connection 객체
        Returns:
            review_info_result : 글 번호, 리뷰 내용 return (r'type : dict)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-08 (hj885353@gmail.com) : 초기 생성
        """
        review_no = {
            'parameter_review_no' : args[0] # 리뷰 글 번호
        }

        session = Session()

        try:
            # db connection 정상 연결 시
            if session:
                review_info_result = review_service.review_info(review_no, session)

                return review_info_result
            # db connection error
            return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500

        except Exception as e:
            return jsonify({'message' : f'{e}'})

        finally:
            session.close()

    @review_bp.route('/<int:parameter_review_no>', methods = ['POST'], endpoint = 'delete_review')
    @login_required(Session)
    @validate_params(
        Param('parameter_review_no', PATH, int, required = True)
    )
    def delete_review(*args, **kwargs):
        """
        리뷰 내용 삭제 API

        리뷰 삭제 버튼을 눌렀을 때, 해당 글 번호를 path_parameter로 받아 해당 글을 soft delete 처리한다.

        Args:
            review_no : validate_params에서 통과 한 path_parameter.
            session : db connection 객체
        Returns:
            SUCCESS, 200
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-08 (hj885353@gmail.com) : 초기 생성
        """
        review_no = {
            'parameter_review_no' : args[0] # 리뷰 글 번호
        }

        session = Session()

        try:
            # db connection 정상 연결 시
            if session:
                review_service.delete_review(review_no, session)
                # transaction commit
                session.commit()
                return jsonify({'message' : 'SUCCESS'}), 200

            # db connection error
            return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500

        except Exception as e:
            # transaction rollback
            session.rollback()
            return jsonify({'message' : f'{e}'})

        finally:
            session.close()

    return review_bp