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

    @order_app.route('/delivery', methods=['GET'], endpoint='get_orders_in_delivery')
    @validate_params(
        Param('orderStatus',            GET, int, required=True),   # 주문상태
        Param('selectFilter',           GET, str, required=False),  # 검색 키워드 주제
        Param('filterKeyword',          GET, str, required=False),  # 검색 키워드
        Param('filterOrder',            GET, str, required=False),  # 정렬기준 : 주문일순 or 주문일역순
        Param('filterLimit',            GET, int, required=False),  # 참조하는 최대 주문정보 갯수
        Param('filterDateFrom',         GET, str, required=False),  # 주문시간 구간조건
        Param('filterDateTo',           GET, str, required=False),  # 주문시간 구간조건
        Param('filterDeliveryNumber',   GET, int, required=False),  # 운송장번호
        Param('page',                   GET, int, required=False),  # 페이지네이션
        Param('mdSeNo',                 GET, list,required=False),  # 셀러속성
    )
    def get_orders_in_delivery(*args, **kwargs):
        
        """
        주문관리 엔드포인트 
        결제완료/상품준비중/배송중/배송완료상태의 주문들에 대한 정보들을 조회하는 엔드포인트 입니다. 
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
        """

        select_condition = {
            'orderStatus'           : args[0], # 주문상태
            'selectFilter'          : args[1], # 검색 키워드 주제
            'filterKeyword'         : args[2], # 검색 키워드
            'filterOrder'           : args[3], # 정렬기준 : 주문일순 or 주문일역순
            'filterLimit'           : args[4], # 참조하는 최대 주문정보 갯수
            'filterDateFrom'        : args[5], # 주문시간 구간조건
            'filterDateTo'          : args[6], # 주문시간 구간조건
            'filterDeliveryNumber'  : args[7], # 운송장번호
            'page'                  : args[8], # 페이지네이션
            'mdSeNo'                : args[9]  # 셀러속성
        }

        try:
            # 세션 인스턴스 생성
            session = Session()

            # 비즈니스 로직 호출
            payment_complete_orders = order_service.get_order_list(select_condition, session)

            return jsonify({'orders': [dict(order) for order in payment_complete_orders]}), 200

        except TimeoutError:
            # DB connection timeout error
            return jsonify({'ERROR_MSG': 'DB_CONNECTION_TIMEOUT'}), 500

        except Exception as e:
            # global error handling
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()

    @order_app.route('/refund', methods=['GET'], endpoint='get_refund_orders')
    @validate_params(
        Param('orderStatus',            GET, int, required=True),   # 주문상태
        Param('selectFilter',           GET, str, required=False),  # 검색 키워드 주제
        Param('filterKeyword',          GET, str, required=False),  # 검색 키워드
        Param('filterOrder',            GET, str, required=False),  # 정렬기준 : 주문일순 or 주문일역순
        Param('filterLimit',            GET, int, required=False),  # 참조하는 최대 주문정보 갯수
        Param('filterDateFrom',         GET, str, required=False),  # 주문시간 구간조건
        Param('filterDateTo',           GET, str, required=False),  # 주문시간 구간조건
        Param('filterRefndReason',      GET, int, required=False),  # 환불사유
        Param('filterCancelReason',     GET, int, required=False),  # 주문취소사유
        Param('page',                   GET, int, required=False),  # 페이지네이션
        Param('mdSeNo',                 GET, list,required=False),  # 셀러속성
    )
    def get_refund_orders(*args, **kwargs):
        
        """
        취소/환불관리 엔드포인트 
        환불요청/환불완료/주문취소완료 상태의 주문들에 대한 정보들을 조회하는 엔드포인트 입니다. 
        특정 상태의 주문 검색시 검색 조건들을 쿼리파라미터로 받고
        해당 조건에 만족하는 주문을 frontend에게 전달합니다.

        args :
        validate_params() 유효성 검사를 통과한 쿼리파라미터

        returns :
        200: 취소/환불관리 주문 리스트
        500: DB_CONNECTION_TIMEOUT, ERROR, SERVICEERROR

        Authors:
        eymin1259@gmail.com 이용민

        History:
        2020-09-24 (이용민) : 초기 생성
        """

        select_condition = {
            'orderStatus'           : args[0], # 주문상태
            'selectFilter'          : args[1], # 검색 키워드 주제
            'filterKeyword'         : args[2], # 검색 키워드
            'filterOrder'           : args[3], # 정렬기준 : 주문일순 or 주문일역순
            'filterLimit'           : args[4], # 참조하는 최대 주문정보 갯수
            'filterDateFrom'        : args[5], # 주문시간 구간조건
            'filterDateTo'          : args[6], # 주문시간 구간조건
            'filterRefndReason'     : args[7], # 환불사유
            'filterCancelReason'    : args[8], # 주문취소사유
            'page'                  : args[9], # 페이지네이션
            'mdSeNo'                : args[10] # 셀러속성
        }

        try:
            # 세션 인스턴스 생성
            session = Session()

            # 비즈니스 로직 호출
            payment_complete_orders = order_service.get_order_list(select_condition, session)

            return jsonify({'orders': [dict(order) for order in payment_complete_orders]}), 200

        except TimeoutError:
            # DB connection timeout error
            return jsonify({'ERROR_MSG': 'DB_CONNECTION_TIMEOUT'}), 500

        except Exception as e:
            # global error handling
            return jsonify({'ERROR_MSG': f'{e}'}), 500

        finally:
            # session close, transaction 종료
            session.close()

            
    return order_app
