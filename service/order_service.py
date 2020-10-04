from custom_error.service_error import ServiceError
import datetime

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
        # return self.order_dao.select_orders(select_condition, session)
        order_list = self.order_dao.select_orders(select_condition, session)
        print(order_list)
        result_order_list = []

        for order in order_list:
            print(order)
            dict_order = dict(order)
            print(dict_order)
            dict_order['option_info'] = f"{dict_order['option_color']} / {dict_order['option_size']}"
            result_order_list.append(dict_order)

        print(result_order_list)
        return result_order_list

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
        """
        주문상세정보 수정 로직
            주문상세번호(order_item_id)를 가지고 해당 주문의 상세정보를 수정하는 DAO 메소드 호출
        
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

        # order table 수정
        if changement.get('ordererPhone', None) or changement.get('receiverPhone', None) or changement.get('address', None) :
            self.order_dao.update_order_info(changement, session)
        
        # order_item_info table 수정
        if changement.get('refundBank', None) or changement.get('refundAccountNum', None) or changement.get('refundAccountHolder', None) or changement.get('shippingCompany', None) or changement.get('shippingNumber', None):
            self.order_dao.update_order_item_info(changement, session)

    def change_order_status(self, next_status_order_list, session):

        """
        주문상태변경 비즈니스 로직
            주문상태변경 주문리스트를 받아서 각각의 주문에 대해 이전상태를 종료하는 DAO 메소드와
            새로운 주문처리상태의 이력을 생성하는 DAO 메소드 호출합니다.
        
        args :
            cancel_order_list : 주문상태변경 주문리스트
            sess              : connection 형성된 session 객체

        Authors:
            eymin1259@gmail.com 이용민
        
        History:
            2020-10-02 (이용민) : 초기 생성
        """

        # 비즈니스로직 트랜잭션 실행 시간
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for next_status_order in next_status_order_list:
            # 현재 이력 종료
            self.order_dao.end_record(next_status_order, now, session)
            # 새로운 주문상태의 row 생성
            self.order_dao.insert_new_status_order_item(next_status_order, now, session)
        

    def cancel_order(self, cancel_order_list, session):

        """
        주문취소처리 비즈니스 로직
            주문취소처리 주문리스트를 받아서 각각의 주문에 대해 이전상태를 종료하는 DAO 메소드와
            새로운 주문처리상태의 이력을 생성하는 DAO 메소드 호출합니다.
        
        args :
            cancel_order_list : 주문취소처리 주문리스트
            sess              : connection 형성된 session 객체

        Authors:
            eymin1259@gmail.com 이용민
        
        History:
            2020-09-29 (이용민) : 초기 생성
        """

        # 비즈니스로직 트랜잭션 실행 시간
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for cancel_order in cancel_order_list:
            # 현재 이력 종료
            self.order_dao.end_record(cancel_order, now, session)
            # 주문취소상태 이력 생성
            self.order_dao.insert_cancel_order_item(cancel_order, now, session)

    def refund_request_order(self, refund_request_list, session):
        
        """
        환불요청 비즈니스 로직
            환불요청 주문리스트를 받아서 각각의 주문에 대해 이전상태를 종료하는 DAO 메소드와
            새로운 환불요청상태의 이력을 생성하는 DAO 메소드 호출합니다.
        
        args :
            cancel_order_list : 환불요청 주문리스트
            sess              : connection 형성된 session 객체

        Authors:
            eymin1259@gmail.com 이용민
        
        History:
            2020-10-02 (이용민) : 초기 생성
        """

        # 비즈니스로직 트랜잭션 실행 시간
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for refund_request in refund_request_list:
            # 현재 이력 종료
            self.order_dao.end_record(refund_request, now, session)
            # 환불요청상태 이력 생성
            self.order_dao.insert_refund_request_order_item(refund_request, now, session)

    def refund_complete_order(self, refund_complete_list, session):

        """
        환불완료 비즈니스 로직
            환불완료 주문리스트를 받아서 각각의 주문에 대해 이전상태를 종료하는 DAO 메소드와
            새로운 환불완료상태의 이력을 생성하는 DAO 메소드 호출합니다.
        
        args :
            cancel_order_list : 환불완료 주문리스트
            sess              : connection 형성된 session 객체

        Authors:
            eymin1259@gmail.com 이용민
        
        History:
            2020-10-02 (이용민) : 초기 생성
        """

        # 비즈니스로직 트랜잭션 실행 시간
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for refund_complete in refund_complete_list:
            # 현재 이력 종료
            self.order_dao.end_record(refund_complete, now, session)
            # 환불완료상태 이력 생성
            self.order_dao.insert_refund_complete_order_item(refund_complete, now, session)

