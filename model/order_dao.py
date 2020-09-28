from flask import jsonify

class OrderDao:

    def select_orders(self, select_condition, session):
        """
        주문 조회
            인자로 받은 주문 검색 조건들을 만족하는 주문들을 데이터베이스에소 조회합니다

        args :
            select_condition : 주문 검색에 필요한 조건들
            sess : connection 형성된 session 객체

        returns :
            검색조건에 해당하는 주문정보 리스트

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-09-23 (이용민) : 초기 생성
            2020-09-26 (이용민) : mysql optimizer가 key를 이용하여 JOIN 하도록 JOIN문 수정
            2020-09-26 (이용민) : 값이 None인지 아닌지 판별하는 if문에서 함수를 사용하여 판별
        """

        # 검색 필터 조건 적용 전 쿼리문
        query = """ SELECT 
                        orders.payment_date,
                        recent_order_item_info.shipping_start_date,
                        recent_order_item_info.shipping_complete_date,
                        recent_order_item_info.refund_request_date,
                        recent_order_item_info.refund_complete_date,
                        recent_order_item_info.complete_cancellation_date,
                        orders.id AS order_id,,
                        recent_order_item_info.order_detail_id,
                        recent_order_item_info.id AS order_item_id,
                        recent_seller_info.korean_name,
                        recent_product_info.name,
                        recent_order_item_info.option_color,
                        recent_order_item_info.option_size,
                        recent_order_item_info.option_additional_price,
                        recent_order_item_info.units,
                        orders.orderer_name,
                        orders.orderer_phone,
                        recent_order_item_info.shipping_number,
                        recent_order_item_info.shipping_company,
                        orders.total_payment,
                        recent_order_item_info.discount_price,
                        recent_order_item_info.refund_reason_id,
                        recent_order_item_info.cancel_reason_id,
                        recent_order_item_info.refund_amount,
                        order_status.status_name

                    FROM orders

                    JOIN order_item_info AS recent_order_item_info
                    ON recent_order_item_info.order_id = orders.id
                    AND recent_order_item_info.end_date = '9999-12-31 23:59:59'   

                    JOIN order_status
                    ON order_status.id = recent_order_item_info.order_status_id

                    JOIN product_info AS recent_product_info 
                    ON recent_product_info.product_id = recent_order_item_info.product_id
                    AND recent_product_info.is_deleted = 0 
                    
                    JOIN seller_info AS recent_seller_info 
                    ON recent_seller_info.seller_id = recent_product_info.seller_id   
                    AND recent_seller_info.end_date = '9999-12-31 23:59:59'
                                            
                """
 
        # 검색 조건 검사
        condition_statement = ''

        # 주문 상태 조건
        # 1 : 결제완료, 2 : 상품준비중, 3 : 배송중, 4 : 배송완료, 5 : 환불요청, 6 : 환불완료, 7 : 주문취소완료
        condition_statement += f"WHERE recent_order_item_info.order_status_id = {select_condition['orderStatus']}"

        # 검색조건
        if select_condition.get('selectFilter', None):
            # 주문번호
            if select_condition['selectFilter'] == 'C_ORDER_CD':
                condition_statement += f" AND recent_order_item_info.order_id LIKE '%{select_condition['filterKeyword']}%'"
            # 주문상세번호
            elif select_condition['selectFilter'] == 'C_ORDER_DETAIL_CD':
                condition_statement += f" AND recent_order_item_info.order_detail_id LIKE '%{select_condition['filterKeyword']}%'"
            # 주문자명
            elif select_condition['selectFilter'] == 'C_ORDER_NAME':
                condition_statement += f" AND orders.orderer_name LIKE '%{select_condition['filterKeyword']}%'"
            # 핸드폰번호
            elif select_condition['selectFilter'] == 'C_ORDER_TELNO':
                condition_statement += f" AND orders.orderer_phone LIKE '%{select_condition['filterKeyword']}%'"
            # 셀러명
            elif select_condition['selectFilter'] == 'C_MD_KO_NAME':
                condition_statement += f" AND recent_seller_info.korean_name LIKE '%{select_condition['filterKeyword']}%'"
            # 상품명
            elif select_condition['selectFilter'] == 'C_PRODUCT_NAME':
                condition_statement += f" AND recent_product_info.name LIKE '%{select_condition['filterKeyword']}%'"

        # 운송장번호 검색
        if select_condition.get('filterDeliveryNumber', None):
            condition_statement += f" AND shipping_orders.shipping_number LIKE '%{select_condition['filterDeliveryNumber']}%'"

        # 환불사유
        if select_condition.get('filterRefndReason', None):
            condition_statement += f" AND refund_cancel_orders.refund_reason_id = {select_condition['filterRefndReason']}"

        # 주문취소사유
        if select_condition.get('filterCancelReason', None):
            condition_statement += f" AND refund_cancel_orders.cancel_reason_id = {select_condition['filterCancelReason']}"

        # 주문완료일 조건 : 시작구간
        if select_condition.get('filterDateFrom', None):
            condition_statement += f" AND orders.payment_date >= '{select_condition['filterDateFrom']}'"

        # 주문완료일 조건 : 종료구간
        if select_condition.get('filterDateTo', None):
            condition_statement += f" AND orders.payment_date <= '{select_condition['filterDateTo']}'"

        # 셀러속성 필터조건
        if select_condition.get('mdSeNo', None):
            if len(select_condition['mdSeNo']) == 1:
                condition_statement += f" AND recent_seller_info.seller_attribute_id = {select_condition['mdSeNo']}"
            else:
                tupled_mdSeNo = tuple(select_condition['mdSeNo'])
                condition_statement += f" AND recent_seller_info.seller_attribute_id IN {tupled_mdSeNo}"

        # 정렬기준
        # 결제일 최신일순
        if select_condition['filterOrder'] == 'NEW':
            condition_statement += " ORDER BY orders.payment_date DESC"
        # 결제일 오래된순
        elif select_condition['filterOrder'] == 'OLD':
            condition_statement += " ORDER BY orders.payment_date ASC"
        # 배송시작 최신일순
        elif select_condition['filterOrder'] == 'NEW_DELIVERY':
            condition_statement += " ORDER BY shipping_orders.shipping_start_date DESC"
        # 배송시작 역순
        elif select_condition['filterOrder'] == 'OLD_DELIVERY':
            condition_statement += " ORDER BY shipping_orders.shipping_start_date ASC"
        # 배송완료 최신일순
        elif select_condition['filterOrder'] == 'NEW_DELIVERY_COMPLETE':
            condition_statement += " ORDER BY shipping_orders.shipping_complete_date DESC"
        # 배송완료 역순
        elif select_condition['filterOrder'] == 'OLD_DELIVERY_COMPLETE':
            condition_statement += " ORDER BY shipping_orders.shipping_complete_date ASC"
        # 최신환불요청일순
        elif select_condition['filterOrder'] == 'NEW_REQUEST_REFUND':
            condition_statement += " ORDER BY refund_cancel_orders.refund_request_date DESC"
        # 환불요청일의 역순
        elif select_condition['filterOrder'] == 'OLD_REQUEST_REFUND':
            condition_statement += " ORDER BY refund_cancel_orders.refund_request_date ASC"
        # 최신환불완료일순
        elif select_condition['filterOrder'] == 'NEW_REFUND_COMPLETE':
            condition_statement += " ORDER BY refund_cancel_orders.refund_complete_date DESC"
        # 환불완료일의 역순
        elif select_condition['filterOrder'] == 'OLD_REFUND_COMPLETE':
            condition_statement += " ORDER BY refund_cancel_orders.refund_complete_date ASC"
        # 최신 주문취소완료일순
        elif select_condition['filterOrder'] == 'NEW_CANCEL_COMPLETE':
            condition_statement += " ORDER BY refund_cancel_orders.complete_cancellation_date DESC"
        # 주문취소완료일의 역순
        elif select_condition['filterOrder'] == 'OLD_CANCEL_COMPLETE':
            condition_statement += " ORDER BY refund_cancel_orders.complete_cancellation_date ASC"

        # 페이지네이션
        if select_condition.get('filterLimit', None):
            if select_condition.get('page', None):
                offset = select_condition['page'] * select_condition['filterLimit']
                condition_statement += f" LIMIT {select_condition['filterLimit']} OFFSET {offset}"
            else:
                condition_statement += f" LIMIT {select_condition['filterLimit']}"

        query += condition_statement

        # query 실행
        rows = session.execute(query).fetchall()

        return rows


    def select_order_detatil_info(self, order_item_id, session):
        """
        주문상세정보 조회 로직
            주문상세번호에 해당하는 주문의 상세정보를 데이터베이스에서 조회
        
        args :
            order_id : 주문상세번호
            sess     : connection 형성된 session 객체

        returns :
            검색조건에 해당하는 주문의 상세정보
         
        Authors:
            eymin1259@gmail.com 이용민
        
        History:
            2020-09-28 (이용민) : 초기 생성
        """

        # 검색 필터 조건 적용 전 쿼리문
        query = """ SELECT 
                        orders.payment_date,
                        recent_order_item_info.shipping_start_date,
                        recent_order_item_info.shipping_complete_date,
                        recent_order_item_info.refund_request_date,
                        recent_order_item_info.refund_complete_date,
                        recent_order_item_info.complete_cancellation_date,
                        orders.id AS order_id,
                        recent_order_item_info.id AS order_item_id,
                        recent_order_item_info.order_detail_id,
                        recent_seller_info.korean_name,
                        recent_product_info.name,
                        recent_order_item_info.option_color,
                        recent_order_item_info.option_size,
                        recent_order_item_info.option_additional_price,
                        recent_order_item_info.units,
                        orders.user_id,
                        orders.orderer_name,
                        orders.orderer_phone,
                        recent_order_item_info.shipping_number,
                        recent_order_item_info.shipping_company,
                        orders.receiver_name,
                        orders.receiver_phone,
                        orders.receiver_address,
                        orders.shipping_memo,
                        orders.total_payment,
                        recent_order_item_info.discount_price,
                        recent_order_item_info.refund_reason_id,
                        recent_order_item_info.cancel_reason_id,
                        recent_order_item_info.refund_amount,
                        order_status.status_name

                    FROM orders

                    JOIN order_item_info AS recent_order_item_info
                    ON recent_order_item_info.order_id = orders.id
                    AND recent_order_item_info.end_date = '9999-12-31 23:59:59'   

                    JOIN product_info AS recent_product_info 
                    ON recent_product_info.product_id = recent_order_item_info.product_id
                    AND recent_product_info.is_deleted = 0 
                    
                    JOIN seller_info AS recent_seller_info 
                    ON recent_seller_info.seller_id = recent_product_info.seller_id   
                    AND recent_seller_info.end_date = '9999-12-31 23:59:59'

                    WHERE recent_order_item_info.id = :order_item_id                    
            """
        
        # query 실행
        row = session.execute(query, {'order_item_id' : order_item_id}).fetchone()

        return row

    def select_order_histories(self, order_id, session):
        """
        주문수정이력 조회 로직
            주문번호에 해당하는 주문의 수정이력을 데이터베이스에서 조회
        
        args :
            order_id : 주문번호
            sess     : connection 형성된 session 객체

        returns :
            검색조건에 해당하는 주문의 수정이력
         
        Authors:
            eymin1259@gmail.com 이용민
        
        History:
            2020-09-24 (이용민) : 초기 생성
        """
        
        query = """ SELECT 
                        order_status.status_name AS order_status,
                        order_item_info.start_date AS update_date
                    FROM order_item_info
                    JOIN order_status
                    ON order_item_info.order_status_id = order_status.id
                    WHERE order_item_info.order_id = :order_id
                """
        # query 실행
        rows = session.execute(query, {'order_id' : order_id}).fetchall()
        
        return rows

    def update_order_info(self, changement, session):
        """
        주문정보 수정 로직
            주문번호에 해당하는 주문정보를 수정
        
        args :
            changement : 수정 내용
            sess       : connection 형성된 session 객체

        Authors:
            eymin1259@gmail.com 이용민
        
        History:
            2020-09-28 (이용민) : 초기 생성
        """

        query = """ UPDATE
                        orders
                    SET
                """
        set_statement = ''
        if changement.get('ordererPhone', None):
            set_statement += ' orderer_phone = :orderer_phone,'

        if changement.get('receiverPhone', None) :
            set_statement += ' receiver_phone = :receiver_phone,'

        if changement.get('address', None) :      
            set_statement += ' receive_address = :receive_address'
        else:
            set_statement = set_statement[:-1]
        
        query += set_statement
        query += ' WHERE id = :order_id'
        
        session.execute(query, {
            'orderer_phone'   : changement['ordererPhone'],
            'receiver_phone'  : changement['receiverPhone'],
            'receive_address' : changement['address'],
            'order_id'        : changement['orderId']})

    def update_order_item_info(self, changement, session):
        """
        주문상세정보 수정 로직
            주문상세번호에 해당하는 주문정보를 수정
        
        args :
            changement : 수정 내용
            sess       : connection 형성된 session 객체

        Authors:
            eymin1259@gmail.com 이용민
        
        History:
            2020-09-28 (이용민) : 초기 생성
        """

        query = """ UPDATE
                        order_item_info
                    SET
                """
        set_statement = ''

        if changement.get('refundBank', None):
            set_statement += ' bank = :bank,'

        if changement.get('refundAccountNum', None) :
            set_statement += ' account_number = :account_number,'

        if changement.get('refundAccountHolder', None) :
            set_statement += ' account_holder = :account_holder,'

        if changement.get('shippingCompany', None) :
            set_statement += ' shipping_company = :shipping_company,'

        if changement.get('shippingNumber', None) :      
            set_statement += ' shipping_number = :shipping_number'
        else:
            set_statement = set_statement[:-1]
        
        query += set_statement
        query += ' WHERE id = :order_item_info_id'
        
        session.execute(query, {
            'bank'               : changement['refundBank'],
            'account_number'     : changement['refundAccountNum'],
            'account_holder'     : changement['refundAccountHolder'],
            'shipping_company'   : changement['shippingCompany'],
            'shipping_number'    : changement['shippingNumber'],
            'order_item_info_id' : changement['orderItemId']})