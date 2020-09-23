from flask import jsonify


class OrderDao:

    def select_payment_complete_orders(self, select_condition, sess):
 
        # 검색 필터 조건 적용 전 쿼리문
        query = """ SELECT 
                        orders.payment_date,
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
                        recent_seller_info.seller_attribute_id 
                    FROM orders
                    INNER JOIN ( SELECT * FROM order_item_info WHERE end_date = '9999-12-31 23:59:59') AS recent_order_item_info ON recent_order_item_info.order_id = orders.id
                    INNER JOIN shipping_orders ON recent_order_item_info.id = shipping_orders.order_item_info_id
                    INNER JOIN ( SELECT * FROM product_info WHERE is_deleted = 0 ) AS recent_product_info ON recent_product_info.product_id = recent_order_item_info.product_id
                    INNER JOIN ( SELECT * FROM seller_info WHERE end_date = '9999-12-31 23:59:59') AS recent_seller_info ON recent_seller_info.seller_id = recent_product_info.seller_id                        WHERE recent_order_item_info.order_status_id = 1
                """

        # 검색 조건 검사
        condition_statement = ''

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

        # 주문완료일 조건 : 시작구간
        if select_condition['filterDateFrom'] != None:
            condition_statement += f" AND orders.payment_date >= '{select_condition['filterDateFrom']}'"

        # 주문완료일 조건 : 종료구간
        if select_condition['filterDateTo'] != None:
            condition_statement += f" AND orders.payment_date <= '{select_condition['filterDateTo']}'"

        # 셀러속성 필터조건
        if select_condition['mdSeNo'] != None:
            tupled_mdSeNo = tuple([select_condition['mdSeNo']])
            condition_statement += f" AND recent_seller_info.seller_attribute_id IN {tupled_mdSeNo}"

        # 정렬기준
        #최신일순
        if select_condition['filterOrder'] == 'NEW': 
            condition_statement += " ORDER BY orders.payment_date DESC"
        #오래된순
        else: 
            condition_statement += " ORDER BY orders.payment_date ASC"
            
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