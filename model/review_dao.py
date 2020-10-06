from flask           import jsonify

class ReviewDao:
    def get_review_list(self, valid_param, session):
        select_review_statement = """
            SELECT 
                r.id as review_id,
                si.korean_name,
                p.id as product_id,
                pi.name as product_name,
                u.login_id,
                r.content,
                r.created_at,
                r.updated_at
            FROM reviews as r
            LEFT JOIN order_item_info as oii ON r.order_item_info_id = oii.id
            LEFT JOIN products as p ON oii.product_id = p.id
            LEFT JOIN product_info as pi ON p.id = pi.product_id
            LEFT JOIN users as u ON r.user_id = u.id
            LEFT JOIN seller_info as si ON pi.seller_id = si.seller_id
            WHERE si.is_deleted = 0
            AND p.is_deleted = 0
            AND pi.is_deleted = 0
            AND u.is_deleted = 0
        """

        filter_query_values_count_statement = """
            SELECT 
                COUNT(0) as filtered_review_count
            FROM reviews as r
            LEFT JOIN order_item_info as oii ON r.order_item_info_id = oii.id
            LEFT JOIN products as p ON oii.product_id = p.id
            LEFT JOIN product_info as pi ON p.id = pi.product_id
            LEFT JOIN users as u ON r.user_id = u.id
            LEFT JOIN seller_info as si ON pi.seller_id = si.seller_id
            WHERE si.is_deleted = 0
            AND p.is_deleted = 0
            AND pi.is_deleted = 0
            AND u.is_deleted = 0
        """

        # 글 내용
        if valid_param.get('REVIEW_TEXT', None):
            select_review_statement += " AND r.content = :REVIEW_TEXT"
            filter_query_values_count_statement += " AND r.content = :REVIEW_TEXT"

        # 글 번호
        if valid_param.get('PRODUCT_INQRY_NO', None):
            select_review_statement += " AND r.id = :PRODUCT_INQRY_NO"
            filter_query_values_count_statement += " AND r.id = :PRODUCT_INQRY_NO"

        # 셀러명
        if valid_param.get('MEMBER_NAME', None):
            select_review_statement += " AND u.login_id = :MEMBER_NAME"
            filter_query_values_count_statement += " AND u.login_id = :MEMBER_NAME"

        # 등록일. ~부터 ~까지
        if valid_param.get('registStartDate', None) and valid_param.get('registEndDate', None):
            select_review_statement += " AND date_format(r.created_at, '%Y-%m-%d %h:%i %p') BETWEEN :registStartDate AND :registEndDate"
            filter_query_values_count_statement += " AND date_format(r.created_at, '%Y-%m-%d %h:%i %p') BETWEEN :registStartDate AND :registEndDate"

        # 수정일. ~부터 ~까지
        if valid_param.get('updateStartDate', None) and valid_param.get('updateEndDate', None):
            select_review_statement += " AND date_format(r.updated_at, '%Y-%m-%d %h:%i %p') BETWEEN :updateStartDate AND :updateEndDate"
            filter_query_values_count_statement += " AND date_format(r.updated_at, '%Y-%m-%d %h:%i %p') BETWEEN :updateStartDate AND :updateEndDate"

        # 등록일시 최신순
        if valid_param.get('NEW_REGIST', None):
            select_review_statement += " ORDER BY created_at DESC"
            filter_query_values_count_statement += " ORDER BY created_at DESC"

        # 수정일시 최신순
        if valid_param.get('NEW_EDIT', None):
            select_review_statement += " ORDER BY updated_at DESC"
            filter_query_values_count_statement += " ORDER BY updated_at DESC"

        select_review_statement += " ORDER BY r.id DESC LIMIT :limit OFFSET :offset"

        # 10개씩 보기, 20개씩 보기
        if valid_param.get('filterLimit', None):
            select_review_statement += " Limit = :filterLimit"
            filter_query_values_count_statement += " Limit = :filterLimit"

        review_lists = session.execute(select_review_statement, valid_param).fetchall()
        review_list = [ dict(review) for review in review_lists ]

        review_count_statement = """
            SELECT 
                COUNT(0) as total_review_count
            FROM reviews as r
            LEFT JOIN order_item_info as oii ON r.order_item_info_id = oii.id
            LEFT JOIN products as p ON oii.product_id = p.id
            LEFT JOIN product_info as pi ON p.id = pi.product_id
            LEFT JOIN users as u ON r.user_id = u.id
            LEFT JOIN seller_info as si ON pi.seller_id = si.seller_id
            WHERE si.is_deleted = 0
            AND p.is_deleted = 0
            AND pi.is_deleted = 0
            AND u.is_deleted = 0
        """
        review_count = dict(session.execute(review_count_statement).fetchone())

        # 필터링 된 count를 fetch 및 dictionary로 casting
        filter_query_values_count = dict(session.execute(filter_query_values_count_statement, valid_param).fetchone())

        # fetch해서 가져온 값을 dictionary에 add
        review_count['filtered_review_count'] = filter_query_values_count['filtered_review_count']
        
        return review_list, review_count