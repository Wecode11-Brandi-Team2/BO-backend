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

# order API


def create_order_endpoints(order_service, Session):
    order_app = Blueprint('order_app', __name__, url_prefix='/api/order')

    @order_app.route('/filter', methods=['GET'], endpoint='get_order_list')
    @validate_params(
        Param('orderStatus',            GET, int, required=True),   # 주문상태
        Param('selectFilter',           GET, str, required=False),  # 검색 키워드 주제
        Param('filterKeyword',          GET, str, required=False),  # 검색 키워드
        Param('filterOrder',            GET, str, required=False),  # 정렬기준 : 주문일순 or 주문일역순
        Param('filterLimit',            GET, int, required=False),  # 참조하는 최대 주문정보 갯수
        Param('filterDateFrom',         GET, str, required=False),  # 주문시간 구간조건
        Param('filterDateTo',           GET, str, required=False),  # 주문시간 구간조건
        Param('filterDeliveryNumber',   GET, int, required=False),  # 운송장번호
        Param('filterRefndReason',      GET, int, required=False),  # 환불사유
        Param('filterCancelReason',     GET, int, required=False),  # 주문취소사유
        Param('page',                   GET, int, required=False),  # 페이지네이션
        Param('mdSeNo',                 GET, list,required=False),  # 셀러속성
    )
    def get_order_list(*args, **kwargs):
        
        """
        주문관리 엔드포인트 
            결제완료/상품준비중/배송중/배송완료환불요청/환불완료/주문취소완료 상태의 주문들에 대한 정보들을 조회하는 엔드포인트 입니다. 
            특정 상태의 주문 검색시 검색 조건들을 쿼리파라미터로 받고
            해당 조건에 만족하는 주문을 frontend에게 전달합니다.

        args :
            validate_params() 유효성 검사를 통과한 쿼리파라미터

        returns :
            200: 결제완료주문 리스트
            500: DB_CONNECTION_TIMEOUT, ERROR, SERVICEERROR

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-09-22 (이용민) : 초기 생성
            2020-09-24 (이용민) : 결제완료/상품준비중/배송중/배송완료상태 엔드포인트 통합
            2020-09-28 (이용민) : 결제완료/상품준비중/배송중/배송완료환불요청/환불완료/주문취소완료 엔드포인트 통합
        """

        # 세션 인스턴스 생성 : connection open, transaction begin
        session = Session()

        try:
            select_condition = {
                'orderStatus'           : args[0], # 주문상태
                'selectFilter'          : None if args[1] == '' else args[1], # 검색 키워드 주제
                'filterKeyword'         : None if args[2] == '' else args[2], # 검색 키워드
                'filterOrder'           : None if args[3] == '' else args[3], # 정렬기준 : 주문일순 or 주문일역순
                'filterLimit'           : args[4], # 참조하는 최대 주문정보 갯수
                'filterDateFrom'        : None if args[5] == '' else args[5], # 주문시간 구간조건
                'filterDateTo'          : None if args[6] == '' else args[6], # 주문시간 구간조건
                'filterDeliveryNumber'  : args[7], # 운송장번호
                'filterRefndReason'     : args[8], # 주문환불이유
                'filterCancelReason'    : args[9], # 주문취소이유
                'page'                  : args[10], # 페이지네이션
                'mdSeNo'                : args[11]  # 셀러속성
            }

            # 비즈니스 로직 호출
            payment_complete_orders = order_service.get_order_list(select_condition, session)

            return jsonify({'orders': [ dict(order) for order in payment_complete_orders]}), 200

        except TimeoutError:
            # DB connection timeout error
            return jsonify({'ERROR_MSG': 'DB_CONNECTION_TIMEOUT'}), 500

        except Exception as e:
            # global error handling
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()

    @order_app.route('/detail/<int:order_item_id>', methods=['GET'], endpoint='get_order_detail_info')
    @validate_params(
        Param('order_item_id', PATH, int, required=True),   # 주문상세번호
    )

    def get_order_detail_info(*args, **kwargs):
        """
        주문상세정보 조회 엔드포인트 
            주문 상세 정보를 조회하는 엔드포인트 입니다. 
            주문상세번호를 url parameter로 전달받고 해당 주문의 상세 정보를 frontend에게 전달합니다.

        args :
            validate_params() 유효성 검사를 통과한 url parameter

        returns :
            200: 주문상세정보
            500: DB_CONNECTION_TIMEOUT, ERROR

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-09-28 (이용민) : 초기 생성
        """
        # 세션 인스턴스 생성 : connection open, transaction begin
        session = Session()
        try:
            # validation check된 주문상세번호
            order_item_id = args[0]
            
            # 주문상세정보 조회 비즈니스로직 호출
            order_detail_info, order_history = order_service.get_order_detail_info(order_item_id, session)
  
            # response body 생성
            response = {
                'order': order_detail_info,
                'history': order_history
            }

            return jsonify(response), 200
                
        except TimeoutError:
            # DB connection timeout error
            return jsonify({'ERROR_MSG': 'DB_CONNECTION_TIMEOUT'}), 500

        except Exception as e:
            # global error handling
            session.rollback()
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()


    @order_app.route('/updateOrderDetail', methods=['PUT'], endpoint='update_order_detail_info')
    @validate_params(
        Param('orderId',                JSON, int, required=False), # 주문 번호
        Param('orderItemId',            JSON, int, required=False), # 주문 상세 번호
        Param('ordererPhone',           JSON, str, required=False), # 주문자 핸드폰 번호
        Param('receiverPhone',          JSON, str, required=False), # 수령자 핸드폰 번호
        Param('address',                JSON, str, required=False), # 수령지 주소
        Param('refundBank',             JSON, str, required=False), # 환불 계좌 은행
        Param('refundAccountNum',       JSON, str, required=False), # 환불 계좌 번호
        Param('refundAccountHolder',    JSON, str, required=False), # 환불 계좌주
        Param('shippingCompany',        JSON, str, required=False), # 배송 택배사
        Param('shippingNumber',         JSON, int, required=False)  # 배송 운송장번호
    )
    def update_order_detail_info(*args, **kwargs):
        """
        주문상세정보 수정 엔드포인트 
            주문상세정보를 수정하는 엔드포인트 입니다. 
            주문 상세 번호와 수정내역을 인자로 전달 받아서 해당 주문의 데이터베이스 정보를 업데이트 합니다

        args :
            validate_params() 유효성 검사를 통과한 수정내역

        returns :
            200: 주문상세정보 수정 성공 메세지
            500: DB_CONNECTION_TIMEOUT, ERROR

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-09-28 (이용민) : 초기 생성
        """

        # 세션 인스턴스 생성 : connection open, transaction begin
        session = Session()

        try:
            # validation check된 수정내역
            changement = {
                'orderId'             : args[0], # 주문번호
                'orderItemId'         : args[1], # 주문 상세 번호
                'ordererPhone'        : None if args[2] == '' else args[2], # 주문자 핸드폰 번호
                'receiverPhone'       : None if args[3] == '' else args[3], # 수령자 핸드폰 번호
                'address'             : None if args[4] == '' else args[4], # 수령지 주소
                'refundBank'          : None if args[5] == '' else args[5], # 환불 계좌 은행
                'refundAccountNum'    : None if args[6] == '' else args[6], # 환불 계좌 번호
                'refundAccountHolder' : None if args[7] == '' else args[7], # 환불 계좌주
                'shippingCompany'     : None if args[8] == '' else args[8], # 배송 택배사
                'shippingNumber'      : args[9]  # 배송 운송장 번호
            }
            
            # 주문상세정보 조회 비즈니스로직 호출
            order_service.update_order_detail_info(changement, session)
            session.commit()

            return jsonify({'MESSAGE': 'UPDATE_SUCCESS' }), 200

        except TimeoutError:
            # DB connection timeout error
            return jsonify({'ERROR_MSG': 'DB_CONNECTION_TIMEOUT'}), 500

        except Exception as e:
            # global error handling
            session.rollback()
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()
    
    # 주문상태변경
    @order_app.route('/changeOrderStatus', methods=['POST'], endpoint='change_order_status')
    @validate_params(
        Param('orderItemId',       JSON, list, required=True), # 주문 상세 번호
        Param('nextOrderStatusId', JSON, int,  required=True), # 다음 주문 상태
    )
    def change_order_status(*args, **kwargs):

        """
        주문상태변경 엔드포인트 
            상품준비처리/배송중처리/배송완료처리/구매확정처리/환불요청취소 처리를 수행하는 엔드포인트 입니다.
            선분이력관리를 위해 이전 상태의 주문의 이력을 종료시키고 새로운 상태의 주문을 데이터베이스에 생성합니다.

        args :
            validate_params() 유효성 검사를 통과한 주문취소정보

        returns :
            200: 주문상태변경 성공메세지
            500: DB_CONNECTION_TIMEOUT, ERROR

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-02 (이용민) : 초기 생성
        """

        # 세션 인스턴스 생성 : connection open, transaction begin
        session = Session()

        try:

            # 주문상태 변경하고싶은 주문리스트 생성 : [{주문1}, {주문2}, ... ]
            # 원소 = {주문상세번호, 다음주문상태}            
            next_status_order_list = []

            for count in range (0, len(args[0])):
                next_status_order_list.append({
                    'order_item_id'        : args[0][count], # 주문 상세 번호
                    'next_order_status_id' : args[1]         # 다음 주문 상태 
                })
            

            # 주문상태변경 비즈니스 로직 호출
            order_service.change_order_status(next_status_order_list, session)

            session.commit()

            return jsonify({'MESSAGE': 'CHANGE_ORDER_STATUS_SUCCESS' }), 200
            
        except TimeoutError:
            # DB connection timeout error
            return jsonify({'ERROR_MSG': 'DB_CONNECTION_TIMEOUT'}), 500

        except Exception as e:
            # global error handling
            session.rollback()
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()

    # 주문취소처리
    @order_app.route('/cancelOrder', methods=['POST'], endpoint='cancel_order')
    @validate_params(
        Param('orderItemId',  JSON, list, required=True),  # 주문 상세 번호
        Param('cancelReason', JSON, list, required=True),  # 주문 취소 이유
    )
    def cancel_order(*args, **kwargs):
        """
        주문취소처리 엔드포인트 
            결제완료/상품준비 상태의 주문을 주문취소처리하는 엔드포인트 입니다.
            선분이력관리를 위해 이전 상태의 주문의 이력을 종료시키고 새로운 상태의 주문을 데이터베이스에 생성합니다.

        args :
            validate_params() 유효성 검사를 통과한 주문취소정보

        returns :
            200: 주문취소처리 성공메세지
            500: DB_CONNECTION_TIMEOUT, ERROR

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-09-29 (이용민) : 초기 생성
        """

        # 세션 인스턴스 생성 : connection open, transaction begin
        session = Session()

        try:

            # 주문취소처리 하려는 주문 갯수
            cancel_order_num = len(args[0])

            # 주문취소처리 하고싶은 주문리스트 생성 : [{주문1}, {주문2}, ... ]
            # 원소 = {주문상세번호, 주문취소이유}
            cancel_order_list = []

            # 주문별로 주문상세번호와 주문취소이유 재 그룹화
            for count in range(0, cancel_order_num):
                cancel_order_list.append({
                    'order_item_id'    : args[0][count], # n번째 주문취소처리 주문상세번호
                    'cancel_reason_id' : args[1][count], # n번째 주문취소처리 주문취소이유
                    'order_status_id'  : 6               # 주문취소완료 상태
                })

            # 주문취소처리 비즈니스 로직 호출
            order_service.cancel_order(cancel_order_list, session)

            session.commit()

            return jsonify({'MESSAGE': 'CANCEL_ORDER_SUCCESS' }), 200

        except TimeoutError:
            # DB connection timeout error
            return jsonify({'ERROR_MSG': 'DB_CONNECTION_TIMEOUT'}), 500

        except Exception as e:
            # global error handling
            session.rollback()
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()

    # 배송중, 배송완료 -> 환불요청
    @order_app.route('/refundRequest', methods=['POST'], endpoint='refund_request')
    @validate_params(
        Param('orderItemId',        JSON, list, required=True), # 주문 상세 번호
        Param('refundReasonId',     JSON, list, required=True), # 주문 환불 이유
        Param('refundReasonDetail', JSON, list, required=True), # 상세 환불 이유
        Param('refundAmount',       JSON, list, required=True), # 환불금액
    )
    def refund_request(*args, **kwargs):
        
        """
        환불요청 엔드포인트 
            배송중/배송완료 상태의 주문에 대해 환불요청 처리를 수행하는 엔드포인트 입니다.
            선분이력관리를 위해 이전 상태의 주문의 이력을 종료시키고 새로운 상태의 주문을 데이터베이스에 생성합니다.

        args :
            validate_params() 유효성 검사를 통과한 주문취소정보

        returns :
            200: 환불요청 성공메세지
            500: DB_CONNECTION_TIMEOUT, ERROR

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-02 (이용민) : 초기 생성
        """

        # 세션 인스턴스 생성 : connection open, transaction begin
        session = Session()

        try:
            # 환불요청처리 하려는 주문 갯수
            refund_request_num = len(args[0])

            # 환불요청처리 하고싶은 주문리스트 생성 : [{주문1}, {주문2}, ... ]
            # 원소 = {주문상세번호, 환불이유, 환불금액, ... }
            refund_request_list = []

            # 환불요청정보를 주문별로 재그룹화
            for count in range(0, refund_request_num):
                refund_request_list.append({
                  'order_item_id'       : args[0][count],   # 주문 상세 번호
                  'refund_reason_id'     : args[1][count],  # 주문 환불 이유
                  'refund_detail_reason' : args[2][count],  # 상세 환불 이유
                  'refund_amount'        : args[3][count],  # 환불금액 
                  'order_status_id'      : 7                # 환불요청
                })

            # 환불요청처리 비즈니스 로직 호출
            order_service.refund_request_order(refund_request_list, session)

            session.commit()

            return jsonify({'MESSAGE': 'REFUND_REQUEST_SUCCESS' }), 200

        except TimeoutError:
            # DB connection timeout error
            return jsonify({'ERROR_MSG': 'DB_CONNECTION_TIMEOUT'}), 500

        except Exception as e:
            # global error handling
            session.rollback()
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()

    # 환불요청 -> 환불완료 : 최종환불
    @order_app.route('/refundComplete', methods=['POST'], endpoint='refund_complete')
    @validate_params(
        Param('orderItemId', JSON, list, required=True), # 주문 상세 번호
    )
    def refund_complete(*args, **kwargs):
        
        """
        환불완료 엔드포인트 
            환불요청 상태의 주문에 대해 환불완료 처리를 수행하는 엔드포인트 입니다.
            선분이력관리를 위해 이전 상태의 주문의 이력을 종료시키고 새로운 상태의 주문을 데이터베이스에 생성합니다.

        args :
            validate_params() 유효성 검사를 통과한 주문취소정보

        returns :
            200: 환불완료 성공메세지
            500: DB_CONNECTION_TIMEOUT, ERROR

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-02 (이용민) : 초기 생성
        """

        # 세션 인스턴스 생성 : connection open, transaction begin
        session = Session()

        try:
            # 환불요청처리 하려는 주문 갯수
            refund_complete_num = len(args[0])

            # 환불요청처리 하고싶은 주문리스트 생성 : [{주문1}, {주문2}, ... ]
            # 원소 = {주문상세번호, 환불이유, 환불금액, ... }
            refund_complete_list = []

            # 환불요청정보를 주문별로 재그룹화
            for count in range(0, refund_complete_num):
                refund_complete_list.append({
                  'order_item_id'   : args[0][count],  # 주문 상세 번호
                  'order_status_id' : 8                # 환불완료 상태
                })

            # 환불요청처리 비즈니스 로직 호출
            order_service.refund_complete_order(refund_complete_list, session)

            session.commit()

            return jsonify({'MESSAGE': 'REFUND_REQUEST_COMPLETE_SUCCESS' }), 200

        except TimeoutError:
            # DB connection timeout error
            return jsonify({'ERROR_MSG': 'DB_CONNECTION_TIMEOUT'}), 500

        except Exception as e:
            # global error handling
            session.rollback()
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()

    return order_app
