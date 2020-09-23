from flask import jsonify

class OrderService:
    def __init__(self, order_dao):
        self.order_dao = order_dao

    def get_payment_complete_order_list(self, select_condition, sess):
        """
        결제완료주문 로직 구현
        결제완료주문 검색시 필요한 조건을 order_dao.select_payment_complete_orders에 전달하여
        쿼리 결과를 controller에게 전달
        
        args :
        select_condition : 결제완료주문 검색에 필요한 조건들
        sess : connection 형성된 session 객체
        
        returns :
        검색조건에 해당하는 결제완료주문정보 리스트
         
        Authors:
        eymin1259@gmail.com 이용민
        
        History:
        2020-09-22 (이용민): 초기 생성
        """
        
        return self.order_dao.select_payment_complete_orders(select_condition, sess)