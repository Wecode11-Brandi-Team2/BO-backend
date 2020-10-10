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
        # except KeyError:
        #     # error 발생 시 transaction rollback
        #     session.rollback()
        #     return jsonify({'MESSAGE' : 'KEY ERROR'}), 400
        #
        # except Exception as e:
        #     # error 발생 시 transaction rollback
        #     session.rollback()
        #     return jsonify({'MESSAGE' : f'{e}'})

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
    @login_required(Session)
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
        seller_info = g.seller_info

        # 데이터베이스 커넥션을 열어줌.
        try:
            session = Session()
            if session:
                seller_list_result = seller_service.get_seller_list(valid_param, seller_info, session)
                # tuple unpacking
                seller_list, seller_count = seller_list_result
                return jsonify({'seller_list' : seller_list, 'seller_count' : seller_count})
            else:
                return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500

        except Exception as e:
            return jsonify({'message': f'{e}'}), 500

        finally:
            session.close()

    @seller_bp.route('/<int:parameter_seller_no>', methods=['GET'], endpoint='get_seller_info')
    @login_required(Session)
    @validate_params(
        Param('parameter_seller_no', PATH, int, required = False)
    )
    def get_seller_info(*args, **kwargs):
        """ 계정의 셀러정보 표출
        path parameter로 seller_no 를 받고 해당 seller의 정보를 표출해 줌

        Args:
            seller_info: seller 정보
            session: db connection 객체
        Returns:
            seller_info_result (r'type : dict)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-09-30 (hj885353@gmail.com) : 초기 생성
        """
        # 로그인 데코레이터에서 받아 온 정보를 dict 형태로 저장해줌
        seller_info = {
            'parameter_seller_no' : args[0],
            'seller_info' : g.seller_info
        }
        session = Session()
        try:
            # db connection 정상 연결 시
            if session:
                seller_info_result = seller_service.get_seller_info(seller_info, session)

                return seller_info_result
            # db connection error
            return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500

        except Exception as e:
            return jsonify({'message' : f'{e}'})

        finally:
            session.close()

    @seller_bp.route('/<int:parameter_seller_no>', methods=['PUT'], endpoint='change_seller_info')
    @login_required(Session)
    @validate_params(
        Param('parameter_seller_no', PATH, int, required = False)
    )
    def change_seller_info(*args, **kwargs):
        """
        path parameter로 seller_id 를 받는다. 
        client로부터 받는 request를 받는다.
        로그인 데코레이터에서 g 객체를 사용하여 해당 seller에 대한 info를 받아 해당 데이터를 service에 전달한다.

        Args:
            validate_params 데코레이터를 통과 한 값을 인자로 받음
        Returns:
            INSERT SUCCESS, 200
            DB_CONNECTION_ERROR, 500
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-01 (hj885353@gmail.com) : 초기 생성
        """
        data = request.json
        change_seller_info = {
            'parameter_seller_no': args[0],
            'seller_data'        : data,
            'seller_info'        : g.seller_info
        }

        session = Session()
        try:
            if session:
                change_seller_info_result = seller_service.change_seller_info(change_seller_info, session)
                session.commit()
                return jsonify({'message' : 'SUCCESS'}), 200

            return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500

        except Exception as e:
            session.rollback()
            return jsonify({'message' : f'{e}'})

        finally:
            session.close()

    @seller_bp.route('check_kor', methods=['GET'], endpoint='check_duplication_kor')
    @login_required(Session)
    def check_duplication_kor():
        """
        셀러 정보 수정 관리 중 한글 셀러명을 변경할 때 셀러명에 대한 중복 검사를 실시하는 함수

        Args:
            
        Returns:
            사용 가능한 한글 셀러명: USABLE, 200
            중복인 한글 셀러명: DUPLICATED_NAME, 400
            DB_CONNECTION_ERROR, 500
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-02 (hj885353@gmail.com) : 초기 생성
            2020-10-07 (hj885353@gmail.com)
                기존 : DB의 한글 셀러명을 모두 다 가져와서 list에 append 후 존재하는지 look up 하는 로직
                변경 : DB에 request로 넘어온 한글 셀러명이 존재하는지 count로 확인. 존재하는 경우 count = 1, 존재하지 않는 경우 count = 0. 이걸로 판별하도록 변경
        """
        kor_name = request.json

        session = Session()

        try:
            if session:
                # service의 check_duplication_kor 함수로 전달
                check_duplication_result = seller_service.check_duplication_kor(kor_name, session)

                # rowcount == 0인 경우. 즉, DB에 일치하는 한글 셀러명이 없을 경우
                if check_duplication_result == 0:
                    return jsonify({'message' : 'USABLE_NAME'}), 200
                # 이미 사용중인 한글 셀러명일 경우
                return jsonify({'message' : 'DUPLICATED_NAME'}), 400

            return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500
        
        except Exception as e:
            return jsonify({'message' : f'{e}'})

        finally:
            session.close()

    @seller_bp.route('check_eng', methods=['GET'], endpoint='check_duplication_eng')
    @login_required(Session)
    def check_duplication_eng():
        """
        셀러 정보 수정 관리 중 영문 셀러명을 변경할 때 셀러명에 대한 중복 검사를 실시하는 함수

        Args:
            
        Returns:
            사용 가능한 영문 셀러명: USABLE, 200
            중복인 영문 셀러명: DUPLICATED_NAME, 400
            DB_CONNECTION_ERROR, 500
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-02 (hj885353@gmail.com) : 초기 생성
            2020-10-07 (hj885353@gmail.com)
                기존 : DB의 영문 셀러명을 모두 다 가져와서 list에 append 후 존재하는지 look up 하는 로직
                변경 : DB에 request로 넘어온 영문 셀러명이 존재하는지 count로 확인. 존재하는 경우 count = 1, 존재하지 않는 경우 count = 0. 이걸로 판별하도록 변경
        """
        eng_name = request.json

        session = Session()

        try:
            if session:
                # service의 check_duplication_eng 함수로 전달
                check_duplication_result = seller_service.check_duplication_eng(eng_name, session)

                # rowcount == 0인 경우. 즉, DB에 일치하는 영문 셀러명이 없을 경우
                if check_duplication_result == 0:
                    return jsonify({'message' : 'USABLE_NAME'}), 200
                # 이미 사용중인 영문 셀러명일 경우
                return jsonify({'message' : 'DUPLICATED_NAME'}), 400

            return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500
        
        except Exception as e:
            return jsonify({'message' : f'{e}'})

        finally:
            session.close()

    @seller_bp.route('/<int:parameter_seller_no>/password', methods=['PUT'], endpoint='change_password')
    @login_required(Session)
    @validate_params(
        Param('parameter_seller_no', PATH, int, required = False),
        Param('original_password', JSON, str, required = False),
        Param('new_password', JSON, str, required = False)
    )
    def change_password(*args, **kwargs):
        # 변경할 비밀번호, 비밀번호 재입력
        change_info = {
            'parameter_seller_no': args[0],
            'original_password'  : args[1],
            'new_password'       : args[2],
            'seller_info'        : g.seller_info
        }
        session = Session()

        try:
            if session:
                change_password_result = seller_service.change_password(change_info, session)
                session.commit()
                return jsonify({'message' : 'SUCCESS'}), 200
            
            return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500
        
        except Exception as e:
            session.rollback()
            return jsonify({'message' : f'{e}'})

        finally:
            session.close()

    return seller_bp