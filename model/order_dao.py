from flask import jsonify


class OrderDao:

    def select_delivery_orders(self, select_condition, sess):
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
        2020-09-23 (이용민): 초기 생성
        """

        # 검색 필터 조건 적용 전 쿼리문
        query = """ SELECT 
                        orders.payment_date,
                        shipping_orders.shipping_start_date,
                        shipping_orders.shipping_complete_date,
                        orders.id,
                        recent_order_item_info.order_detail_id,
                        recent_seller_info.korean_name,
                        recent_product_info.name,
                        recent_order_item_info.option_color,
                        recent_order_item_info.option_size,
                        recent_order_item_info.option_additional_price,
                        recent_order_item_info.units,
                        orders.orderer_name,
                        orders.orderer_phone,
                        orders.total_payment,
                        recent_order_item_info.discount_price,
                        recent_order_item_info.order_status_id

                    FROM orders

                    INNER JOIN ( SELECT * FROM order_item_info WHERE end_date = '9999-12-31 23:59:59') AS recent_order_item_info 
                    ON recent_order_item_info.order_id = orders.id

                    INNER JOIN shipping_orders 
                    ON recent_order_item_info.id = shipping_orders.order_item_info_id

                    INNER JOIN ( SELECT * FROM product_info WHERE is_deleted = 0 ) AS recent_product_info 
                    ON recent_product_info.product_id = recent_order_item_info.product_id

                    INNER JOIN ( SELECT * FROM seller_info WHERE end_date = '9999-12-31 23:59:59') AS recent_seller_info 
                    ON recent_seller_info.seller_id = recent_product_info.seller_id                        
                """

        # 검색 조건 검사
        condition_statement = ''

        # 주문 상태 조건
        # 1 : 결제완료, 2 : 상품준비중, 3 : 배송중, 4 : 배송완료
        condition_statement += f"WHERE recent_order_item_info.order_status_id = {select_condition['orderStatus']}"

        # 검색조건
        if select_condition['selectFilter'] != None:
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
        if select_condition['filterDeliveryNumber'] != None:
            condition_statement += f" AND shipping_orders.shipping_number LIKE '%{select_condition['filterDeliveryNumber']}%'"

        # 주문완료일 조건 : 시작구간
        if select_condition['filterDateFrom'] != None:
            condition_statement += f" AND orders.payment_date >= '{select_condition['filterDateFrom']}'"

        # 주문완료일 조건 : 종료구간
        if select_condition['filterDateTo'] != None:
            condition_statement += f" AND orders.payment_date <= '{select_condition['filterDateTo']}'"

        # 셀러속성 필터조건
        if select_condition['mdSeNo'] != None:
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

        # 페이지네이션
        if select_condition['filterLimit'] != None:
            if select_condition['page'] == None:
                condition_statement += f" LIMIT {select_condition['filterLimit']}"
            else:
                offset = select_condition['page'] * select_condition['filterLimit']
                condition_statement += f" LIMIT {select_condition['filterLimit']} OFFSET {offset}"

        query += condition_statement

        # query 실행, database engine으로부터 connection 생성 및 transaction 시작
        rows = sess.execute(query)

        return rows

        def select_refund_orders(self, select_condition, sess):
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
            2020-09-24 (이용민): 초기 생성
            """

            # 검색 필터 조건 적용 전 쿼리문
            query = """ SELECT 
                            orders.payment_date,
                            refund_cancel_orders.shipping_start_date,
                            refund_cancel_orders.refund_request_date,
                            refund_cancel_orders.refund_complete_date,
                            refund_cancel_orders.complete_cancellation_date,
                            orders.id,
                            recent_order_item_info.order_detail_id,
                            recent_seller_info.korean_name,
                            recent_product_info.name,
                            recent_order_item_info.option_color,
                            recent_order_item_info.option_size,
                            recent_order_item_info.option_additional_price,
                            recent_order_item_info.units,
                            orders.orderer_name,
                            orders.orderer_phone,
                            refund_cancel_orders.refund_reason_id,
                            refund_cancel_orders.cancel_reason_id,
                            refund_cancel_orders.refund_amount,
                            recent_order_item_info.order_status_id

                        FROM orders

                        INNER JOIN ( SELECT * FROM order_item_info WHERE end_date = '9999-12-31 23:59:59') AS recent_order_item_info 
                        ON recent_order_item_info.order_id = orders.id

                        INNER JOIN refund_cancel_orders 
                        ON recent_order_item_info.id = refund_cancel_orders.order_item_info_id

                        INNER JOIN ( SELECT * FROM product_info WHERE is_deleted = 0 ) AS recent_product_info 
                        ON recent_product_info.product_id = recent_order_item_info.product_id

                        INNER JOIN ( SELECT * FROM seller_info WHERE end_date = '9999-12-31 23:59:59') AS recent_seller_info 
                        ON recent_seller_info.seller_id = recent_product_info.seller_id                        
                    """
            # 검색 조건 검사
            condition_statement = ''

            # 주문 상태 조건
            # 5 : 환불요청, 6 : 환불완료, 7 : 주문취소완료
            condition_statement += f"WHERE recent_order_item_info.order_status_id = {select_condition['orderStatus']}"

            # 검색조건
            if select_condition['selectFilter'] != None:
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
        
            # 환불사유
            if select_condition['filterRefndReason'] != None:
                condition_statement += f" AND refund_cancel_orders.refund_reason_id = {select_condition['filterRefndReason']}"

            # 주문취소사유
            if select_condition['filterCancelReason'] != None:
                condition_statement += f" AND refund_cancel_orders.cancel_reason_id = {select_condition['filterCancelReason']}"

            # 주문완료일 조건 : 시작구간
            if select_condition['filterDateFrom'] != None:
                condition_statement += f" AND orders.payment_date >= '{select_condition['filterDateFrom']}'"

            # 주문완료일 조건 : 종료구간
            if select_condition['filterDateTo'] != None:
                condition_statement += f" AND orders.payment_date <= '{select_condition['filterDateTo']}'"

            # 셀러속성 필터조건
            if select_condition['mdSeNo'] != None:
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
            if select_condition['filterLimit'] != None:
                if select_condition['page'] == None:
                    condition_statement += f" LIMIT {select_condition['filterLimit']}"
                else:
                    offset = select_condition['page'] * select_condition['filterLimit']
                    condition_statement += f" LIMIT {select_condition['filterLimit']} OFFSET {offset}"

            query += condition_statement

            # query 실행, database engine으로부터 connection 생성 및 transaction 시작
            rows = sess.execute(query)

            return rows

