from flask           import jsonify
from sqlalchemy import text

class QnADao:
    def get_qna_list(self, valid_param, seller_info, session):
        """
        Q&A list를 보여주는 함수
        service로부터 인자를 전달받고, db로부터 조건을 만족하는 리뷰 목록과 갯수를 조회해서 return

        Args:
            valid_param : QueryString Validation을 통과 한 dict
            seller_info : seller_info를 담고 있음
            session : db connection 객체
        Returns:
            qna_list : 조건을 충족하는 Q&A 목록을 db에서 조회하여 service로 return (r'type : tuple)
            qna_count : 조건을 충족하는 Q&A 갯수를 db에서 count하여 service로 return (r'type : tuple)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-05 (hj885353@gmail.com) : 초기 생성
        """
        # db로부터 Q&A 목록 반환해주는데 필요한 field를 조회하는 쿼리문
        get_qna_list_statement = """
            SELECT
                q.id as question_id,
                qt.type_name,
                q.created_at,
                u.phone_number,
                pi.name,
                si.korean_name,
                q.content,
                u.id as user_id
            FROM questions as q
            INNER JOIN question_types as qt ON qt.id = q.type_id
            INNER JOIN answers as a
            INNER JOIN users as u ON q.user_id = u.id
            INNER JOIN products as p ON p.id = q.product_id
            INNER JOIN product_info as pi ON p.id = pi.product_id
            INNER JOIN sellers as s ON s.id = a.replier_id
            INNER JOIN seller_info as si ON s.id = si.seller_id
            WHERE q.is_deleted = 0
            AND a.is_deleted = 0
            AND u.is_deleted = 0
            AND p.is_deleted = 0
            AND pi.is_deleted = 0
            AND s.is_deleted = 0
        """
        # QueryString으로 필터링 했을 때, 해당 필터링 된 Q&A의 갯수를 count하는 쿼리문
        filter_query_values_count_statement = """
            SELECT 
                COUNT(0) as filtered_qna_count
            FROM questions as q
            INNER JOIN question_types as qt ON qt.id = q.type_id
            INNER JOIN answers as a
            INNER JOIN users as u ON q.user_id = u.id
            INNER JOIN products as p ON p.id = q.product_id
            INNER JOIN product_info as pi ON p.id = pi.product_id
            INNER JOIN sellers as s ON s.id = a.replier_id
            INNER JOIN seller_info as si ON s.id = si.seller_id
            WHERE q.is_deleted = 0
            AND a.is_deleted = 0
            AND u.is_deleted = 0
            AND p.is_deleted = 0
            AND pi.is_deleted = 0
            AND s.is_deleted = 0
        """
        # 상품명
        if valid_param.get('product_name', None):
            get_qna_list_statement += " AND pi.name = :product_name"
            filter_query_values_count_statement += " AND pi.name = :product_name"

        # 글번호
        if valid_param.get('product_inqry_no', None):
            get_qna_list_statement += " AND q.id = :product_inqry_no"
            filter_query_values_count_statement += " AND q.id = :product_inqry_no"

        # 셀러 한글명
        if valid_param.get('md_ko_name', None):
            get_qna_list_statement += " AND si.korean_name = :md_ko_name"
            filter_query_values_count_statement += " AND si.korean_name = :md_ko_name"

        # 회원 번호
        if valid_param.get('order_no', None):
            get_qna_list_statement += " AND s.id = :order_no"
            filter_query_values_count_statement += " AND s.id = :order_no"
        
        # 문의 유형
        if valid_param.get('inquiry_type', None):
            get_qna_list_statement += " AND qt.type_name = :inquiry_type"
            filter_query_values_count_statement += " AND qt.type_name = :inquiry_type"

        # 등록일 ~부터
        if valid_param.get('regist_date_from', None):
            get_qna_list_statement += " AND DATE(q.created_at) >= :regist_date_from"
            filter_query_values_count_statement += " AND DATE(q.created_at) >= :regist_date_from"

        # 등록일 ~까지
        if valid_param.get('regist_date_from', None) and valid_param.get('regist_date_to', None):
            get_qna_list_statement += " AND DATE(q.created_at) BETWEEN :regist_date_from AND :regist_date_to"
            filter_query_values_count_statement += " AND DATE(q.created_at) BETWEEN :regist_date_from AND :regist_date_to"

        # pagination 및 내림차순 정렬
        get_qna_list_statement += " ORDER BY q.id DESC LIMIT :limit OFFSET :offset"
        # Q&A 전체 목록을 다 가져옴
        qna_lists = session.execute(get_qna_list_statement, valid_param).fetchall()
        # dict 형태로 변환
        qna_list = [ dict(qna) for qna in qna_lists ]

        # 전체 Q&A 갯수 count하는 쿼리문
        qna_count_statement = """
            SELECT
                COUNT(q.id) as total_qna_count
            FROM questions as q
            INNER JOIN question_types as qt ON qt.id = q.type_id
            INNER JOIN answers as a
            INNER JOIN users as u ON q.user_id = u.id
            INNER JOIN products as p ON p.id = q.product_id
            INNER JOIN product_info as pi ON p.id = pi.product_id
            INNER JOIN sellers as s ON s.id = a.replier_id
            INNER JOIN seller_info as si ON s.id = si.seller_id
            WHERE q.is_deleted = 0
            AND a.is_deleted = 0
            AND u.is_deleted = 0
            AND p.is_deleted = 0
            AND pi.is_deleted = 0
            AND s.is_deleted = 0
        """

        # 전체 갯수를 count하여 fetch 및 dictionary로 casting
        qna_count = dict(session.execute(qna_count_statement).fetchone())

        # 필터링 된 count를 fetch 및 dictionary로 casting
        filter_query_values_count = dict(session.execute(filter_query_values_count_statement, valid_param).fetchone())

        # fetch해서 가져온 값을 dictionary에 add
        qna_count['filtered_qna_count'] = filter_query_values_count['filtered_qna_count']

        return qna_list, qna_count

        