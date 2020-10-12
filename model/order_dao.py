class OrderDao:

    def select_orders_count(self, select_condition, session):
        """
        주문 갯수 조회
            인자로 받은 검색조건들을 만족하는 주문들의 갯수를 구합니다.

        args :
            select_condition : 주문 검색에 필요한 조건들
            session          : connection 형성된 session 객체

        returns :
            검색조건에 해당하는 주문 갯수

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-08 (이용민) : 초기 생성
        """

        # 검색 필터 조건 적용 전 쿼리문
        query = """ SELECT 
                        count(orders.id)

                    FROM orders

                    INNER JOIN order_item_info AS oi_info
                    ON oi_info.order_id = orders.id
                    AND oi_info.end_date = '9999-12-31 23:59:59'   

                    INNER JOIN product_info AS p_info 
                    ON p_info.product_id = oi_info.product_id
                    AND p_info.is_deleted = 0 

                    INNER JOIN seller_info AS s_info 
                    ON s_info.seller_id = p_info.seller_id   
                    AND s_info.end_date = '9999-12-31 23:59:59'
                """

        # 검색 조건 검사
        condition_statement = ''

        # 주문 상태 조건
        # 1 : 결제완료, 2 : 상품준비중, 3 : 배송중, 4 : 배송완료, 5 : 환불요청, 6 : 환불완료, 7 : 주문취소완료
        condition_statement += f"WHERE oi_info.order_status_id = {select_condition['orderStatus']}"

        # 검색조건
        if select_condition.get('selectFilter', None):
            # 주문번호
            if select_condition['selectFilter'] == 'C_ORDER_CD':
                condition_statement += f" AND oi_info.order_id LIKE '%{select_condition['filterKeyword']}%'"
            # 주문상세번호
            elif select_condition['selectFilter'] == 'C_ORDER_DETAIL_CD':
                condition_statement += f" AND oi_info.order_detail_id LIKE '%{select_condition['filterKeyword']}%'"
            # 주문자명
            elif select_condition['selectFilter'] == 'C_ORDER_NAME':
                condition_statement += f" AND orders.orderer_name LIKE '%{select_condition['filterKeyword']}%'"
            # 핸드폰번호
            elif select_condition['selectFilter'] == 'C_ORDER_TELNO':
                condition_statement += f" AND orders.orderer_phone LIKE '%{select_condition['filterKeyword']}%'"
            # 셀러명
            elif select_condition['selectFilter'] == 'C_MD_KO_NAME':
                condition_statement += f" AND s_info.korean_name LIKE '%{select_condition['filterKeyword']}%'"
            # 상품명
            elif select_condition['selectFilter'] == 'C_PRODUCT_NAME':
                condition_statement += f" AND p_info.name LIKE '%{select_condition['filterKeyword']}%'"

        # 운송장번호 검색
        if select_condition.get('filterDeliveryNumber', None):
            condition_statement += f" oi_info.shipping_number LIKE '%{select_condition['filterDeliveryNumber']}%'"

        # 환불사유
        if select_condition.get('filterRefndReason', None):
            condition_statement += f" AND oi_info.refund_reason_id = {select_condition['filterRefndReason']}"

        # 주문취소사유
        if select_condition.get('filterCancelReason', None):
            condition_statement += f" AND oi_info.cancel_reason_id = {select_condition['filterCancelReason']}"

        # 주문완료일 조건 : 시작구간
        if select_condition.get('filterDateFrom', None):
            condition_statement += f" AND orders.payment_date >= '{select_condition['filterDateFrom']}'"

        # 주문완료일 조건 : 종료구간
        if select_condition.get('filterDateTo', None):
            condition_statement += f" AND orders.payment_date <= '{select_condition['filterDateTo']}'"

        # 셀러속성 필터조건
        if select_condition.get('mdSeNo', None):
            if len(select_condition['mdSeNo']) == 1:
                condition_statement += f" AND s_info.seller_attribute_id = {select_condition['mdSeNo']}"
            else:
                tupled_mdSeNo = tuple(select_condition['mdSeNo'])
                condition_statement += f" AND s_info.seller_attribute_id IN {tupled_mdSeNo}"

        query += condition_statement

        # query 실행
        res = session.execute(query).fetchone()[0]
        return res

    def select_orders(self, select_condition, session):
        """
        주문 조회
            인자로 받은 주문 검색 조건들을 만족하는 주문들을 데이터베이스에소 조회합니다

        args :
            select_condition : 주문 검색에 필요한 조건들
            session          : connection 형성된 session 객체

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
                        oi_info.shipping_start_date,
                        oi_info.shipping_complete_date,
                        oi_info.refund_request_date,
                        oi_info.refund_complete_date,
                        oi_info.complete_cancellation_date,
                        orders.id AS order_id,
                        oi_info.order_detail_id,
                        oi_info.id AS order_item_id,
                        s_info.korean_name AS seller_name,
                        p_info.name AS product_name,
                        oi_info.option_color,
                        oi_info.option_size,
                        oi_info.option_additional_price,
                        oi_info.units,
                        orders.orderer_name,
                        orders.orderer_phone,
                        orders.total_payment,
                        oi_info.discount_price,
                        oi_info.refund_reason_id,
                        oi_info.cancel_reason_id,
                        oi_info.refund_amount

                    FROM orders

                    INNER JOIN order_item_info AS oi_info
                    ON oi_info.order_id = orders.id
                    AND oi_info.end_date = '9999-12-31 23:59:59'   

                    INNER JOIN product_info AS p_info 
                    ON p_info.product_id = oi_info.product_id
                    AND p_info.is_deleted = 0 

                    INNER JOIN seller_info AS s_info 
                    ON s_info.seller_id = p_info.seller_id   
                    AND s_info.end_date = '9999-12-31 23:59:59'
                """

        # 검색 조건 검사
        condition_statement = ''

        # 주문 상태 조건
        # 1 : 결제완료, 2 : 상품준비중, 3 : 배송중, 4 : 배송완료, 5 : 환불요청, 6 : 환불완료, 7 : 주문취소완료
        condition_statement += f"WHERE oi_info.order_status_id = {select_condition['orderStatus']}"

        # 검색조건
        if select_condition.get('selectFilter', None):
            # 주문번호
            if select_condition['selectFilter'] == 'C_ORDER_CD':
                condition_statement += f" AND oi_info.order_id LIKE '%{select_condition['filterKeyword']}%'"
            # 주문상세번호
            elif select_condition['selectFilter'] == 'C_ORDER_DETAIL_CD':
                condition_statement += f" AND oi_info.order_detail_id LIKE '%{select_condition['filterKeyword']}%'"
            # 주문자명
            elif select_condition['selectFilter'] == 'C_ORDER_NAME':
                condition_statement += f" AND orders.orderer_name LIKE '%{select_condition['filterKeyword']}%'"
            # 핸드폰번호
            elif select_condition['selectFilter'] == 'C_ORDER_TELNO':
                condition_statement += f" AND orders.orderer_phone LIKE '%{select_condition['filterKeyword']}%'"
            # 셀러명
            elif select_condition['selectFilter'] == 'C_MD_KO_NAME':
                condition_statement += f" AND s_info.korean_name LIKE '%{select_condition['filterKeyword']}%'"
            # 상품명
            elif select_condition['selectFilter'] == 'C_PRODUCT_NAME':
                condition_statement += f" AND p_info.name LIKE '%{select_condition['filterKeyword']}%'"

        # 운송장번호 검색
        if select_condition.get('filterDeliveryNumber', None):
            condition_statement += f" oi_info.shipping_number LIKE '%{select_condition['filterDeliveryNumber']}%'"

        # 환불사유
        if select_condition.get('filterRefndReason', None):
            condition_statement += f" AND oi_info.refund_reason_id = {select_condition['filterRefndReason']}"

        # 주문취소사유
        if select_condition.get('filterCancelReason', None):
            condition_statement += f" AND oi_info.cancel_reason_id = {select_condition['filterCancelReason']}"

        # 주문완료일 조건 : 시작구간
        if select_condition.get('filterDateFrom', None):
            condition_statement += f" AND orders.payment_date >= '{select_condition['filterDateFrom']}'"

        # 주문완료일 조건 : 종료구간
        if select_condition.get('filterDateTo', None):
            condition_statement += f" AND orders.payment_date <= '{select_condition['filterDateTo']}'"

        # 셀러속성 필터조건
        if select_condition.get('mdSeNo', None):
            if len(select_condition['mdSeNo']) == 1:
                condition_statement += f" AND s_info.seller_attribute_id = {select_condition['mdSeNo']}"
            else:
                tupled_mdSeNo = tuple(select_condition['mdSeNo'])
                condition_statement += f" AND s_info.seller_attribute_id IN {tupled_mdSeNo}"

        # 정렬기준
        # 결제일 최신일순
        if select_condition['filterOrder'] == 'NEW':
            condition_statement += " ORDER BY orders.payment_date DESC"
        # 결제일 오래된순
        elif select_condition['filterOrder'] == 'OLD':
            condition_statement += " ORDER BY orders.payment_date ASC"
        # 배송시작 최신일순
        elif select_condition['filterOrder'] == 'NEW_DELIVERY':
            condition_statement += " ORDER BY oi_info.shipping_start_date DESC"
        # 배송시작 역순
        elif select_condition['filterOrder'] == 'OLD_DELIVERY':
            condition_statement += " ORDER BY oi_info.shipping_start_date ASC"
        # 배송완료 최신일순
        elif select_condition['filterOrder'] == 'NEW_DELIVERY_COMPLETE':
            condition_statement += " ORDER BY oi_info.shipping_complete_date DESC"
        # 배송완료 역순
        elif select_condition['filterOrder'] == 'OLD_DELIVERY_COMPLETE':
            condition_statement += " ORDER BY oi_info.shipping_complete_date ASC"
        # 최신환불요청일순
        elif select_condition['filterOrder'] == 'NEW_REQUEST_REFUND':
            condition_statement += " ORDER BY oi_info.refund_request_date DESC"
        # 환불요청일의 역순
        elif select_condition['filterOrder'] == 'OLD_REQUEST_REFUND':
            condition_statement += " ORDER BY oi_info.refund_request_date ASC"
        # 최신환불완료일순
        elif select_condition['filterOrder'] == 'NEW_REFUND_COMPLETE':
            condition_statement += " ORDER BY oi_info.refund_complete_date DESC"
        # 환불완료일의 역순
        elif select_condition['filterOrder'] == 'OLD_REFUND_COMPLETE':
            condition_statement += " ORDER BY oi_info.refund_complete_date ASC"
        # 최신 주문취소완료일순
        elif select_condition['filterOrder'] == 'NEW_CANCEL_COMPLETE':
            condition_statement += " ORDER BY oi_info.complete_cancellation_date DESC"
        # 주문취소완료일의 역순
        elif select_condition['filterOrder'] == 'OLD_CANCEL_COMPLETE':
            condition_statement += " ORDER BY oi_info.complete_cancellation_date ASC"

        # 페이지네이션
        if select_condition.get('filterLimit', None):
            if select_condition.get('page', None):
                offset = (select_condition['page']-1) * select_condition['filterLimit']
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
            session  : connection 형성된 session 객체

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
                        oi_info.shipping_start_date,
                        oi_info.shipping_complete_date,
                        oi_info.refund_request_date,
                        oi_info.refund_complete_date,
                        oi_info.complete_cancellation_date,
                        orders.id AS order_id,
                        oi_info.id AS order_item_id,
                        oi_info.order_detail_id,
                        s_info.korean_name AS seller_name,
                        p_info.name AS product_name,
                        oi_info.option_color,
                        oi_info.option_size,
                        oi_info.option_additional_price,
                        oi_info.units,
                        orders.user_id,
                        orders.orderer_name,
                        orders.orderer_phone,
                        oi_info.shipping_number,
                        oi_info.shipping_company,
                        orders.receiver_name,
                        orders.receiver_phone,
                        orders.receiver_address,
                        orders.shipping_memo,
                        orders.total_payment,
                        oi_info.discount_price,
                        oi_info.refund_reason_id,
                        oi_info.cancel_reason_id,
                        oi_info.refund_amount,
                        order_status.status_name AS order_status_name

                    FROM orders

                    INNER JOIN order_item_info AS oi_info
                    ON oi_info.order_id = orders.id
                    AND oi_info.end_date = '9999-12-31 23:59:59'   

                    INNER JOIN product_info AS p_info 
                    ON p_info.product_id = oi_info.product_id
                    AND p_info.is_deleted = 0 
                    
                    INNER JOIN seller_info AS s_info 
                    ON s_info.seller_id = p_info.seller_id   
                    AND s_info.end_date = '9999-12-31 23:59:59'

                    INNER JOIN order_status
                    ON order_status.id = oi_info.order_status_id

                    WHERE oi_info.order_detail_id = :order_item_id                    
            """

        # query 실행
        row = session.execute(
            query, {'order_item_id': order_item_id}).fetchone()
        return row

    def select_order_histories(self, order_id, session):
        """
        주문수정이력 조회 로직
            주문번호에 해당하는 주문의 수정이력을 데이터베이스에서 조회

        args :
            order_id : 주문번호
            session  : connection 형성된 session 객체

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
                    INNER JOIN order_status
                    ON order_item_info.order_status_id = order_status.id
                    WHERE order_item_info.order_id = :order_id
                """
        # query 실행
        rows = session.execute(query, {'order_id': order_id}).fetchall()

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

        if changement.get('receiverPhone', None):
            set_statement += ' receiver_phone = :receiver_phone,'

        if changement.get('address', None):
            set_statement += ' receive_address = :receive_address'
        else:
            set_statement = set_statement[:-1]

        query += set_statement
        query += ' WHERE id = :order_id'

        session.execute(query, {
            'orderer_phone': changement['ordererPhone'],
            'receiver_phone': changement['receiverPhone'],
            'receive_address': changement['address'],
            'order_id': changement['orderId']})

    def update_order_item_info(self, changement, session):
        """
        주문상세정보 수정 로직
            주문상세번호에 해당하는 주문정보를 수정

        args :
            changement : 수정 내용
            session    : connection 형성된 session 객체

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

        if changement.get('refundAccountNum', None):
            set_statement += ' account_number = :account_number,'

        if changement.get('refundAccountHolder', None):
            set_statement += ' account_holder = :account_holder,'

        if changement.get('shippingCompany', None):
            set_statement += ' shipping_company = :shipping_company,'

        if changement.get('shippingNumber', None):
            set_statement += ' shipping_number = :shipping_number'
        else:
            set_statement = set_statement[:-1]

        query += set_statement
        query += ' WHERE id = :order_item_info_id'

        session.execute(query, {
            'bank': changement['refundBank'],
            'account_number': changement['refundAccountNum'],
            'account_holder': changement['refundAccountHolder'],
            'shipping_company': changement['shippingCompany'],
            'shipping_number': changement['shippingNumber'],
            'order_item_info_id': changement['orderItemId']})

    def end_record(self, cancel_order, updated_at, session):
        """
        주문 선분이력 종료 처리 로직
            주어진 주문상세번호에 해당하는 최신상태 주문의 선분이력을 종료처리하는 엔드포인트 입니다.

        args :
            cancel_order : 취소할 주문의 주문상세번호 및 취소내용이 담긴 딕셔너리
            updated_at   : 로직이 실행되는 시간

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-09-29 (이용민) : 초기 생성
        """

        query = """ UPDATE 
                        order_item_info 
                    SET 
                        end_date = :updated_at, 
                        is_deletd = 1
                    WHERE 
                        order_item_info.order_detail_id = :order_item_id
                        AND is_delete = 0
                """
        session.execute(query, {
            'updated_at': updated_at,
            'order_item_id': cancel_order['order_item_id']})

    def insert_new_status_order_item(self, next_status_order, updated_at, session):
        """
        주문상태변경 선분이력 생성 로직
            해당 주문상세번호에 전달받은 주문상태로 새로운 row를 생성합니다.        

        args :
            next_status_order : 변경할 주문의 주문상세번호 및 변경내용이 담긴 딕셔너리
            updated_at        : 이력 수정시간

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-02 (이용민) : 초기 생성
        """

        query = """ INSERT INTO 
                        order_item_info 
                            (
                                order_detail_id,
                                order_id,
                                order_status_id,
                                product_id,
                                price,
                                option_color,
                                option_size,
                                option_additional_price,
                                units,
                                discount_price,
                                shipping_start_date,
                                shipping_complete_date,
                                shipping_company,
                                shipping_number,
                                is_confirm_order,
                                refund_request_date,
                                refund_complete_date,
                                refund_reason_id,
                                refund_amount,
                                refund_shipping_fee,
                                detail_reason,
                                bank,
                                account_holder,
                                account_number,
                                cancel_reason_id,
                                complete_cancellation_date,
                                start_date,
                                end_date,
                                modifier_id
                            )
                    SELECT 
                        order_detail_id,
                        order_id,
                        :order_status_id,
                        product_id,
                        price,
                        option_color,
                        option_size,
                        option_additional_price,
                        units,
                        discount_price,
                        shipping_start_date,
                        shipping_complete_date,
                        shipping_company,
                        shipping_number,
                        is_confirm_order,
                        refund_request_date,
                        refund_complete_date,
                        refund_reason_id,
                        refund_amount,
                        refund_shipping_fee,
                        detail_reason,
                        bank,
                        account_holder,
                        account_number,
                        cancel_reason_id,
                        complete_cancellation_date,
                        :updated_at,
                        '9999-12-31 23:59:59',
                        modifier_id
                    FROM
                        order_item_info
                    WHERE
                        order_item_info.order_detail_id = :order_item_id
                        AND end_date = :updated_at
                        AND is_deletd = 1
                """

        session.execute(query, {
            'updated_at': updated_at,
            'order_status_id': next_status_order['next_order_status_id'],
            'order_item_id': next_status_order['order_item_id']
        })

    def insert_cancel_order_item(self, cancel_order, updated_at, session):
        """
        주문취소완료처리 선분이력 생성 로직
            주어진 주문상세번호에 주문에 주문상태가 주문취소완료인 새로운 row를 생성합니다.        

        args :
            cancel_order : 취소할 주문의 주문상세번호 및 취소내용이 담긴 딕셔너리
            updated_at   : 로직이 실행되는 시간

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-09-29 (이용민) : 초기 생성
        """

        # 이전 상태를 복사하여 새로운 주문취소완료상태 주문 생성
        query = """ INSERT INTO 
                        order_item_info 
                            (
                                order_detail_id,
                                order_id,
                                order_status_id,
                                product_id,
                                price,
                                option_color,
                                option_size,
                                option_additional_price,
                                units,
                                discount_price,
                                shipping_start_date,
                                shipping_complete_date,
                                shipping_company,
                                shipping_number,
                                is_confirm_order,
                                refund_request_date,
                                refund_complete_date,
                                refund_reason_id,
                                refund_amount,
                                refund_shipping_fee,
                                detail_reason,
                                bank,
                                account_holder,
                                account_number,
                                cancel_reason_id,
                                complete_cancellation_date,
                                start_date,
                                end_date,
                                modifier_id
                            )
                    SELECT 
                        order_detail_id,
                        order_id,
                        :order_status_id,
                        product_id,
                        price,
                        option_color,
                        option_size,
                        option_additional_price,
                        units,
                        discount_price,
                        shipping_start_date,
                        shipping_complete_date,
                        shipping_company,
                        shipping_number,
                        is_confirm_order,
                        refund_request_date,
                        refund_complete_date,
                        refund_reason_id,
                        refund_amount,
                        refund_shipping_fee,
                        detail_reason,
                        bank,
                        account_holder,
                        account_number,
                        :cancel_reason_id,
                        :updated_at,
                        :updated_at,
                        '9999-12-31 23:59:59',
                        modifier_id
                    FROM
                        order_item_info
                    WHERE
                        order_item_info.order_detail_id = :order_item_id
                        AND end_date = :updated_at
                        AND is_deletd = 1
                """
        session.execute(query, {
            'updated_at': updated_at,
            'order_item_id': cancel_order['order_item_id'],
            'order_status_id': cancel_order['order_status_id'],
            'cancel_reason_id': cancel_order['cancel_reason_id']
        })

    def insert_refund_request_order_item(self, refund_request, updated_at, session):
        """
        환불요청 선분이력 생성 로직
            해당 주문상세번호의 주문에 환불요청상태로 새로운 row를 생성합니다.        

        args :
            refund_request : 환불요청할 주문의 주문상세번호 및 환불요청 내용이 담긴 딕셔너리
            updated_at     : 이력 수정시간

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-02 (이용민) : 초기 생성
        """

        # 이전 상태를 복사하여 새로운 주문환불요청상태 주문 생성
        query = """ INSERT INTO 
                        order_item_info 
                            (
                                order_detail_id,
                                order_id,
                                order_status_id,
                                product_id,
                                price,
                                option_color,
                                option_size,
                                option_additional_price,
                                units,
                                discount_price,
                                shipping_start_date,
                                shipping_complete_date,
                                shipping_company,
                                shipping_number,
                                is_confirm_order,
                                refund_request_date,
                                refund_complete_date,
                                refund_reason_id,
                                refund_amount,
                                refund_shipping_fee,
                                detail_reason,
                                bank,
                                account_holder,
                                account_number,
                                cancel_reason_id,
                                complete_cancellation_date,
                                start_date,
                                end_date,
                                modifier_id
                            )
                    SELECT 
                        order_detail_id,
                        order_id,
                        :order_status_id,
                        product_id,
                        price,
                        option_color,
                        option_size,
                        option_additional_price,
                        units,
                        discount_price,
                        shipping_start_date,
                        shipping_complete_date,
                        shipping_company,
                        shipping_number,
                        is_confirm_order,
                        :updated_at,
                        refund_complete_date,
                        :refund_reason_id,
                        :refund_amount,
                        refund_shipping_fee,
                        :refund_detail_reason,
                        bank,
                        account_holder,
                        account_number,
                        cancel_reason_id,
                        complete_cancellation_date,
                        :updated_at,
                        '9999-12-31 23:59:59',
                        modifier_id
                    FROM
                        order_item_info
                    WHERE
                        order_item_info.order_detail_id = :order_item_id
                        AND end_date = :updated_at
                        AND is_deletd = 1
                """
        session.execute(query, {
            'updated_at': updated_at,
            'order_item_id': refund_request['order_item_id'],
            'order_status_id': refund_request['order_status_id'],
            'refund_reason_id': refund_request['refund_reason_id'],
            'refund_amount': refund_request['refund_amount'],
            'refund_detail_reason': refund_request['refund_detail_reason']
        })

    def insert_refund_complete_order_item(self, refund_complete, updated_at, session):
        """
        환불완료 선분이력 생성 로직
            해당 주문상세번호의 주문에 환불완료 상태로 새로운 row를 생성합니다.        

        args :
            refund_complete : 환불완료할 주문의 주문상세번호 및 환불완료 내용이 담긴 딕셔너리
            updated_at      : 이력 수정시간

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-02 (이용민) : 초기 생성
        """

        query = """ INSERT INTO 
                        order_item_info 
                            (
                                order_detail_id,
                                order_id,
                                order_status_id,
                                product_id,
                                price,
                                option_color,
                                option_size,
                                option_additional_price,
                                units,
                                discount_price,
                                shipping_start_date,
                                shipping_complete_date,
                                shipping_company,
                                shipping_number,
                                is_confirm_order,
                                refund_request_date,
                                refund_complete_date,
                                refund_reason_id,
                                refund_amount,
                                refund_shipping_fee,
                                detail_reason,
                                bank,
                                account_holder,
                                account_number,
                                cancel_reason_id,
                                complete_cancellation_date,
                                start_date,
                                end_date,
                                modifier_id
                            )
                    SELECT 
                        order_detail_id,
                        order_id,
                        :order_status_id,
                        product_id,
                        price,
                        option_color,
                        option_size,
                        option_additional_price,
                        units,
                        discount_price,
                        shipping_start_date,
                        shipping_complete_date,
                        shipping_company,
                        shipping_number,
                        is_confirm_order,
                        refund_request_date,
                        :updated_at,
                        refund_reason_id,
                        refund_amount,
                        refund_shipping_fee,
                        detail_reason,
                        bank,
                        account_holder,
                        account_number,
                        cancel_reason_id,
                        complete_cancellation_date,
                        :updated_at,
                        '9999-12-31 23:59:59',
                        modifier_id
                    FROM
                        order_item_info
                    WHERE
                        order_item_info.order_detail_id = :order_item_id
                        AND end_date = :updated_at
                        AND is_deletd = 1
                """
        session.execute(query, {
            'updated_at': updated_at,
            'order_item_id': refund_complete['order_item_id'],
            'order_status_id': refund_complete['order_status_id']
        })

    def restore_record(self, restore_order, updated_at, session):
        """
        이전 주문상태로 되돌리는 로직
            updated_at 시간에 종료된 상태를 그 이전 상태로 되돌려 새로운 row를 생성합니다.

        args :
            restore_order   : 이전상태로 되돌릴 주문의 주문상세번호 및 주문상태정보가 담긴 딕셔너리
            updated_at      : 이력 수정시간

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-06 (이용민) : 초기 생성
        """

        query = """ INSERT INTO 
                        order_item_info 
                            (
                                order_detail_id,
                                order_id,
                                order_status_id,
                                product_id,
                                price,
                                option_color,
                                option_size,
                                option_additional_price,
                                units,
                                discount_price,
                                shipping_start_date,
                                shipping_complete_date,
                                shipping_company,
                                shipping_number,
                                is_confirm_order,
                                refund_request_date,
                                refund_complete_date,
                                refund_reason_id,
                                refund_amount,
                                refund_shipping_fee,
                                detail_reason,
                                bank,
                                account_holder,
                                account_number,
                                cancel_reason_id,
                                complete_cancellation_date,
                                start_date,
                                end_date,
                                modifier_id
                            )
                    SELECT 
                        order_detail_id,
                        order_id,
                        :order_status_id,
                        product_id,
                        price,
                        option_color,
                        option_size,
                        option_additional_price,
                        units,
                        discount_price,
                        shipping_start_date,
                        shipping_complete_date,
                        shipping_company,
                        shipping_number,
                        is_confirm_order,
                        null,
                        null,
                        null,
                        null,
                        null,
                        null,
                        null,
                        null,
                        null,
                        cancel_reason_id,
                        complete_cancellation_date,
                        :updated_at,
                        '9999-12-31 23:59:59',
                        modifier_id
                    FROM
                        order_item_info
                    WHERE
                        order_item_info.order_detail_id = :order_item_id
                        AND end_date = :updated_at
                        AND is_deletd = 1
                """
        session.execute(query, {
            'updated_at': updated_at,
            'order_item_id': restore_order['order_item_id'],
            'order_status_id': restore_order['restore_order_status_id']
        })
