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

    @order_app.route('/paymentcomplete', methods=['GET'], endpoint='get_payment_complete_orders')
    @validate_params(
        Param('selectFilter',   GET, str, required=False),  # 검색 키워드 주제
        Param('filterKeyword',  GET, str, required=False),  # 검색 키워드
        Param('filterOrder',    GET, str, required=False),  # 정렬기준 : 주문일순 or 주문일역순
        Param('filterLimit',    GET, int, required=False),  # 참조하는 최대 주문정보 갯수
        Param('filterDateFrom', GET, str, required=False),  # 주문시간 구간조건
        Param('filterDateTo',   GET, str, required=False),  # 주문시간 구간조건
        Param('page',           GET, int, required=False),  # 페이지네이션
        Param('mdSeNo',         GET, list, required=False), # 셀러속성

    )
    def get_payment_complete_orders(*args, **kwargs):
        """
        결제완료주문 엔드포인트 
        결제완료상태의 주문들에 대한 정보들을 조회하는 엔드포인트 입니다. 
        결제완료주문들 검색시 검색 조건들을 쿼리파라미터로 받고
        해당 조건에 만족하는 결제완료주문을 frontend에게 전달

        args :
        validate_params() 유효성 검사를 통과한 쿼리파라미터

        returns :
        200: 결제완료주문 리스트
        500: DB_CONNECTION_TIMEOUT, ERROR

        Authors:
        eymin1259@gmail.com 이용민

        History:
        2020-09-22 (이용민): 초기 생성
        """

        select_condition = {
            'selectFilter': args[0],    # 검색 키워드 주제
            'filterKeyword': args[1],   # 검색 키워드
            'filterOrder': args[2],     # 정렬기준 : 주문일순 or 주문일역순
            'filterLimit': args[3],     # 참조하는 최대 주문정보 갯수
            'filterDateFrom': args[4],  # 주문시간 구간조건
            'filterDateTo': args[5],    # 주문시간 구간조건
            'page': args[6],            # 페이지네이션
            'mdSeNo': args[7],          # 셀러속성
        }

        try:
            # 세션 인스턴스 생성
            session = Session()

            # 비즈니스 로직 호출
            payment_complete_orders = order_service.get_payment_complete_order_list(
                select_condition, session)


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
