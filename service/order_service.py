from customerror.service_error import SERVICEERROR

class OrderService:
    def __init__(self, order_dao):
        self.order_dao = order_dao

    def get_order_list(self, select_condition, sess):

        """
        결제완료/상품준비중/배송중/배송완료/환불요청/환불완료/주문취소완료 상태 주문 조회 로직
        주문 상태에 따라 호출할 DAO 메소드를 분류하여 해당 검색 조건을 DAO에 전달합니다.
        쿼리 결과를 controller에게 전달
        
        args :
        select_condition : 주문 검색에 필요한 조건들
        sess : connection 형성된 session 객체
        
        returns :
        검색조건에 해당하는 주문정보 리스트
         
        Authors:
        eymin1259@gmail.com 이용민
        
        History:
        2020-09-22 (이용민) : 초기 생성
        2020-09-24 (이용민) : 주문상태 분류 로직 추가
        """

        #  결제완료/상품준비중/배송중/배송완료상태의 주문들에 대한 정보 조회
        if select_condition['orderStatus'] in [1,2,3,4]:
            return self.order_dao.select_delivery_orders(select_condition, sess)
        
        # 환불요청/환불완료/주문취소완료 상태의 주문들에 대한 정보 조회
        elif select_condition['orderStatus'] in [5,6,7]:
            return self.order_dao.select_refund_orders(select_condition, sess)
        else:
            raise SERVICEERROR("NO_ORDER_STATUS")
