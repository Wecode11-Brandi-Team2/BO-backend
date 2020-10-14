from flask import (
    Blueprint,
    request,
    jsonify
)
from flask_request_validator import (
    GET,
    PATH,
    Param,
    JSON,
    validate_params
)

def create_coupon_endpoints(coupon_service, Session):
    coupon_app = Blueprint('coupon_app', __name__, url_prefix='/api/coupon')

    @coupon_app.route('/list', methods=['GET'], endpoint='get_coupon_list')
    @validate_params(
        Param('couponId',               GET, str, required = False),   # 쿠폰아이디             
        Param('couponName',             GET, str, required = False),   # 쿠폰이름               
        Param('validationStartFrom',    GET, str, required = False),   # 유효시작구간 시작일            
        Param('validationStartTo',      GET, str, required = False),   # 유효시작구간 종료일            
        Param('validationEndFrom',      GET, str, required = False),   # 유효종료구간 시작일        
        Param('validationEndTo',        GET, str, required = False),   # 유효종료구간 종료일        
        Param('downloadStartFrom',      GET, str, required = False),   # 다운로드시작구간 시작일        
        Param('downloadStartTo',        GET, str, required = False),   # 다운로드시작구간 종료일    
        Param('downloadEndFrom',        GET, str, required = False),   # 다운로드종료구간 시작일    
        Param('downloadEndTo',          GET, str, required = False),   # 다운로드종료구간 종료일    
        Param('IssueTypeId',            GET, int, required = False),   # 발급유형               
        Param('IsLimited',              GET, int, required = False),   # 제한여부               
        Param('page',                   GET, int, required = False),   # 페이지네이션                   
    )
    def get_coupon_list(*args, **kwargs):
        """
        쿠폰리스트 조회 엔드포인트 
            쿠폰리스트를 데이터베이스에서 조회하여 쿠폰정보및 갯수 프론트에게 전달하는 엔드포인트입니다.

        returns :
            200: 쿠폰리스트정보

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-06 (이용민) : 초기 생성
        """
        # 세션 인스턴스 생성 : connection open, transaction begin
        session = Session()
        try:

            # 쿠폰 조회 조건
            select_condition = {
                'couponId'            : None if args[0] is None else int(args[0]),  # 쿠폰아이디       
                'couponName'          : None if args[1] == '' else args[1],      # 쿠폰이름         
                'validationStartFrom' : None if args[2] == '' else args[2],      # 유효시작구간 시작일   
                'validationStartTo'   : None if args[3] == '' else args[3],      # 유효시작구간 종료일   
                'validationEndFrom'   : None if args[4] == '' else args[4],      # 유효종료구간 시작일   
                'validationEndTo'     : None if args[5] == '' else args[5],      # 유효종료구간 종료일   
                'downloadStartFrom'   : None if args[6] == '' else args[6],      # 다운로드시작구간 시작일 
                'downloadStartTo'     : None if args[7] == '' else args[7],      # 다운로드시작구간 종료일 
                'downloadEndFrom'     : None if args[8] == '' else args[8],      # 다운로드종료구간 시작일 
                'downloadEndTo'       : None if args[9] == '' else args[9],      # 다운로드종료구간 종료일 
                'issueTypeId'         : None if args[10] == -1 else args[10],    # 발급유형          
                'isLimited'           : None if args[11] == -1 else args[11],    # 제한여부          
                'page'                : args[12] # 페이지네이션        
            }

            # 쿠폰리스트 조회 비즈니스로직 호출
            total_coupon_num = coupon_service.get_coupon_count(select_condition, session)
            coupon_list = coupon_service.get_coupon_list(select_condition, session)
            
            # response body 생성
            response = {
                'total_coupon_num': total_coupon_num,
                'coupons': coupon_list
            }

            return jsonify(response), 200

        except Exception as e:
            # global error handling
            session.rollback()
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()

    # 쿠폰상세정보
    @coupon_app.route('/detail/<int:coupon_id>', methods=['GET'], endpoint='get_coupon_detail')
    @validate_params(
        Param('coupon_id', PATH, int, required=True),   # 쿠폰 아이디
    )
    def get_coupon_detail(*args, **kwargs):
        """
        쿠폰상세정보 조회 엔드포인트
            전달받은 쿠폰아이디에 해당하는 쿠폰상세정보를 데이터베이스에서 조회하여 프론트에게 전달하는 엔드포인트입니다.

        args :
            coupon_id : 쿠폰아이디

        returns :
            200: 쿠폰상세정보

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-06 (이용민) : 초기 생성
        """

        # 세션 인스턴스 생성 : connection open, transaction begin
        session = Session()
        try:

            coupon_id = args[0]
            # 쿠폰리스트 조회 비즈니스로직 호출
            coupon_detail = coupon_service.get_coupon_detail(
                coupon_id, session)
            coupon_detail = dict(coupon_detail)

            return jsonify(coupon_detail), 200

        except Exception as e:
            # global error handling
            session.rollback()
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()

    # 쿠폰등록

    @coupon_app.route('', methods=['POST'], endpoint='insert_coupon')
    @validate_params(
        Param('couponName',             JSON, str, required=True),   # 쿠폰 이름
        Param('coupinIssueMethodId',    JSON, int, required=True),   # 쿠폰 발급방법
        Param('couponIssueTypeId',      JSON, int, required=True),   # 쿠폰 발급유형
        Param('description',            JSON, str, required=False),  # 쿠폰 상세 설명
        Param('downloadStartDate',      JSON, str, required=True),   # 다운로드시작일
        Param('downloadEndDate',        JSON, str, required=True),   # 다운로드종료일
        Param('validationStartDate',    JSON, str, required=True),   # 유효시작일
        Param('validationEndDate',      JSON, str, required=True),   # 유효종료일
        Param('discountPrice',          JSON, int, required=True),   # 할인금액
        Param('isLimited',              JSON, int, required=True),   # 발급제한 여부
        Param('maximumNumber',          JSON, int, required=False),  # 발급제한 갯수
        Param('minCost',                JSON, int, required=True)    # 최소 사용 금액
    )
    def insert_coupon(*args, **kwargs):
        """
        쿠폰등록 엔드포인트
            전달받은 정보를 가지고 쿠폰데이터를 생성하는 엔드포인트입니다.

        args :
            couponName          : 쿠폰이름
            coupinIssueMethodId : 쿠폰 발급방법 
            couponIssueTypeId   : 쿠폰 발급유형
            description         : 쿠폰 상세 설명
            downloadStartDate   : 다운로드시작일
            downloadEndDate     : 다운로드종료일
            validationStartDate : 유효시작일
            validationEndDate   : 유효종료일
            discountPrice       : 할인금액
            isLimited           : 발급제한 여부
            maximumNumber       : 발급제한 갯수
            minCost             : 최소 사용 금액

        returns :
            200: 쿠폰생성 성공메세지
            500 : 에러메시지

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-07 (이용민) : 초기 생성
        """

        # 세션 인스턴스 생성 : connection open, transaction begin
        session = Session()
        try:

            # 쿠폰정보를 넘겨주기 위해 딕셔너리 생성
            coupon_info = {
                'coupon_name': args[0],  # 쿠폰 이름
                'issue_method_id': args[1],  # 쿠폰 발급방법
                'issue_type_id': args[2],  # 쿠폰 발급유형
                'description': args[3],  # 쿠폰 상세 설명
                'download_start_date': args[4],  # 다운로드시작일
                'download_end_date': args[5],  # 다운로드종료일
                'validation_start_date': args[6],  # 유효시작일
                'validation_end_date': args[7],  # 유효종료일
                'discount_price': args[8],  # 할인금액
                'is_limited': args[9],  # 발급제한 여부
                'maximum_number': args[10],  # 발급제한 갯수
                'min_cost': args[11]  # 최소 사용 금액
            }

            # 쿠폰생성 비즈니스로직 호출
            coupon_service.insert_coupon(coupon_info, session)

            session.commit()

            return jsonify({"MESSAGE": "COUPON_INSERT_SUCCESS"}), 200

        except Exception as e:
            # global error handling
            session.rollback()
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()

    # 쿠폰정보수정
    @coupon_app.route('', methods=['PUT'], endpoint='update_coupon')
    @validate_params(
        Param('couponId',    PATH, int, required=True),   # 쿠폰 아이디
        Param('couponName',  PATH, int, required=True),   # 쿠폰이름
        Param('description', PATH, int, required=True),   # 쿠폰상세설명
    )
    def update_coupon(*args, **kwargs):
        """
        쿠폰정보수정 엔드포인트
            전달받은 쿠폰아이디에 해당하는 쿠폰정보를 수정하는 엔드포인트입니다.

        args :
            couponId    : 쿠폰 아이디
            couponName  : 쿠폰이름
            description : 쿠폰 상세 설명

        returns :
            200: 쿠폰수정 성공메세지
            500 : 에러메시지

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-07 (이용민) : 초기 생성
        """

        # 세션 인스턴스 생성 : connection open, transaction begin
        session = Session()
        try:

            # 쿠폰정보를 넘겨주기 위해 딕셔너리 생성
            coupon_info = {
                'coupon_id': args[1],  # 쿠폰아이디
                'coupon_name': args[1],  # 쿠폰 이름
                'description': args[2],  # 쿠폰 상세 설명
            }

            # 쿠폰수정 비즈니스로직 호출
            coupon_service.update_coupon(coupon_info, session)

            session.commit()

            return jsonify({"MESSAGE": "COUPON_UPDATE_SUCCESS"}), 200

        except Exception as e:
            # global error handling
            session.rollback()
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()

    return coupon_app
