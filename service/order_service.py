from custom_error.service_error import ServiceError

class OrderService:
    def __init__(self, order_dao):
        self.order_dao = order_dao

    def get_order_list(self, select_condition, session):

        """
        결제완료/상품준비중/배송중/배송완료/환불요청/환불완료/주문취소완료 상태 주문 조회 로직
            검색 조건을 DAO에 전달하고 반환받은 쿼리 결과를 controller에게 전달합니다.
        
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
            2020-09-28 (이용민) : 주문상태 통합 로직으로 변경
        """
        return self.order_dao.select_orders(select_condition, session)

    def get_order_detail_info(self, order_item_id, session):

        """
        주문상세정보 조회 로직
            주문상세번호(order_item_id)를 가지고 해당 주문의 상세정보와 주문상태변경내역을 controller에게 반환
        
        args :
            order_item_id : 주문상세번호
            sess          : connection 형성된 session 객체

        returns :
            order_detail_info : 검색조건에 해당하는 주문의 상세정보와 상태변경이력
         
        Authors:
            eymin1259@gmail.com 이용민
        
        History:
            2020-09-28 (이용민) : 초기 생성
        """

        # 주문 상세 정보 조회
        order_detail_info = self.order_dao.select_order_detatil_info(order_item_id, session)
        dict_order_detail_info = dict(order_detail_info)
        order_id = dict_order_detail_info['order_id']

        # 주문 수정 내역 조회
        order_history = self.order_dao.select_order_histories(order_id, session)
        order_history_list = [dict(history) for history in order_history]

        return dict_order_detail_info, order_history_list
    
    def update_order_detail_info(self, changement, session):

        if changement.get('ordererPhone', None) or changement.get('receiverPhone', None) or changement.get('address', None) :
            self.order_dao.update_order_info(changement, session)
        if changement.get('refundBank', None) or changement.get('refundAccountNum', None) or changement.get('refundAccountHolder', None) or changement.get('shippingCompany', None) or changement.get('shippingNumber', None):
            self.order_dao.update_order_item_info(changement, session)