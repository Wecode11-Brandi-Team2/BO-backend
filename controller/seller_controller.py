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
from ast import literal_eval
from utils import login_required

def create_seller_endpoints(services, Session):
    seller_service = services
    seller_bp = Blueprint('seller', __name__, url_prefix = '/api/seller')

    """
    seller 회원가입 endpoint

    Args:
        seller_info:
            seller_loginID      : seller login ID,
            password            : seller 회원가입 시 비밀번호,
            korean_name         : 한글 이름,
            eng_name            : 영어 이름,
            service_center_phone: 서비스센터 전화번호,
            site_url            : 셀러 site_url,
            seller_id           : seller table FK로 연결되는 id
            seller_attribute_id : seller_attributes table FK로 연결되는 id
            seller_status_id    : seller_status table FK로 연결되는 id
            manager_id          : manager table FK로 연결되는 id
            modifier_id         : 수정 승인자에 대한 id
        session : db 연결
    Returns:
        200 : 생성된 유저 객체
        400 : KeyError, loginID 중복 발생 시
    Authors:
        hj885353@gmail.com(김해준)
    History:
        2020-09-23 (hj885353@gmail.com) : 초기 생성
    """

    @seller_bp.route('/signup', methods = ['POST'])
    def create_sign_up():
        try:
            # transaction start
            session = Session()

            seller_info       = request.json
            if seller_info['attribute_id'] == 1 or 2 or 3: 
                seller_info['attribute_id'] = 4
            elif seller_info['attribute_id'] == 4 or 5 or 6:
                seller_info['attribute_id'] = 5
            elif seller_info['attribute_id'] == 7:
                seller_info['attribute_id'] = 6

            new_seller_result = seller_service.create_new_seller(seller_info, session)

            # transaction commit
            session.commit()
            return jsonify({'MESSAGE' : 'SUCCESS'}), 200

        # 중복되는 ID를 입력했을 경우의 예외처리
        except exc.IntegrityError:
            # error 발생 시 transaction rollback
            session.rollback()
            return jsonify({'MESSAGE' : 'DUPLICATED ID'}), 400

        # KeyError 발생 시의 예외처리
        except KeyError:
            # error 발생 시 transaction rollback
            session.rollback()
            return jsonify({'MESSAGE' : 'KEY ERROR'}), 400

        except Exception as e:
            # error 발생 시 transaction rollback
            session.rollback()
            return jsonify({'MESSAGE' : f'{e}'})

        finally:
            # transaction close
            session.close()

    @seller_bp.route('/login', methods = ['POST'])
    @validate_params(
        Param('loginID', JSON, str),
        Param('password', JSON, str)
    )
    def login(*args, **kwargs):
        """
        input으로 들어온 ID와 password가 일치했을 경우 token을 발행해주는 함수

        Return:
            access_token 발행, 200
            비밀번호 불일치 시, 401
        Authors:
            hj885353@gmail.com(김해준)
        History:
            2020-09-25 (hj885353@gmail.com) : 초기 생성
        """
        seller_info = {
            'login_id': args[0],
            'password': args[1]
        }
        session = Session()

        try:
            authorized = seller_service.login(seller_info, session)

            # service에서 정상적으로 password 비교가 완료 됐을 경우 if문 동작
            if authorized:
                seller_credential = seller_service.get_seller_id_and_password(seller_info, session)
                access_token      = seller_service.generate_access_token(seller_info, session)

                # transaction commit
                session.commit()

                return jsonify({
                    'access_token' : access_token
                }), 200
            else:
                # service에서 정상적으로 password가 비교가 완료되지 못 했을 경우 401 return
                session.rollback()
                return jsonify({'message' : 'INVALID_USER'}), 401

        except Exception as e:
            # 에러 발생으로 transaction rollback
            session.rollback()

            return jsonify({'error_message' : f'{e}'})

        finally:
            # transaction close
            session.close()

    @seller_bp.route('/sellers', methods=['GET'], endpoint='get_seller_list')
    @login_required
    @validate_params(
        Param('mber_no', GET, int, required = False),
        Param('mber_ncnm', GET, str, required = False),
        Param('mber_en', GET, str, required = False),
        Param('mber_ko', GET, str, required = False),
        Param('manager_name', GET, str, required = False),
        Param('seller_status', GET, int, required = False),
        Param('manager_telno', GET, str, required = False),
        Param('manager_email', GET, str, required = False),
        Param('seller_attribute', GET, int, required = False),
        Param('produdct_count', GET, int, required = False),
        Param('mber_date_from', GET, str, required = False),
        Param('mber_date_to', GET, str, required = False),
        Param('action', GET, str, required = False),
        Param('start_at', GET, str, required = False),
        Param('end_date', GET, str, required = False),
        Param('offset', GET, int, required = False),
        Param('limit', GET, int, required = False)
    )
    def get_seller_list(*args, **kwargs):
        """ 가입된 모든 셀러 정보 리스트 표출
        Args:
            g.loginID: 데코레이터에서 넘겨받은 계정 정보
            args: path parameter 를 통해서 들어온 검색 키워드
        Returns: http 상태 코드
            seller_list, seller_count 정상 response, 200
            db connection error, 500
        Authors:
            hj885353@gmail.com
        History:
            2020-09-28 (hj885353@gmail.com): 초기 생성
        """
        start_at = args[13]
        end_date = args[14]
        # 시작 기간이 종료 기간보다 늦으면 시작기간 = 종료기간
        if start_at and end_date:
            if start_at > end_date:
                start_at = end_date

        # validation 을 통과한 값을 담을 딕셔너리를 만들어줌.
        valid_param = {}

        # valid_param 딕셔너리에 validation 을 통과한 query parameter 을 넣어줌.
        valid_param['mber_no']          = args[0]
        valid_param['mber_ncnm']        = args[1]
        valid_param['mber_en']          = args[2]
        valid_param['mber_ko']          = args[3]
        valid_param['manager_name']     = args[4]
        valid_param['seller_status']    = args[5]
        valid_param['manager_telno']    = args[6]
        valid_param['manager_email']    = args[7]
        valid_param['seller_attribute'] = args[8]
        valid_param['product_count']    = args[9]
        valid_param['mber_date_from']   = args[10]
        valid_param['mber_date_to']     = args[11]
        valid_param['action']           = args[12]
        valid_param['start_at']         = start_at
        valid_param['end_date']         = end_date
        valid_param['limit']            = args[15] if args[15] else 10
        valid_param['offset']           = args[16] if args[16] else 0

        # 유저 정보를 g에서 읽어와서 service 에 전달
        seller_no = g.seller_no

        # 데이터베이스 커넥션을 열어줌.
        try:
            session = Session()
            if session:
                seller_list_result = seller_service.get_seller_list(valid_param, seller_no, session)
                # tuple unpacking
                seller_list, seller_count = seller_list_result
                return jsonify({'seller_list' : seller_list, 'seller_count' : seller_count})
            else:
                return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500

        except Exception as e:
            return jsonify({'message': f'{e}'}), 500

        finally:
            session.close()

    return seller_bp