import math
from flask           import jsonify

class ReviewDao:
    def get_review_list(self, valid_param, session):
        """
        Review list 반환해주는 함수

        필요한 정보를 조회하고, 인자로 받은 valid_param에서 querystring 값을 받아
        해당 querystring에 대한 값을 필터링해서 반환해줍니다.
        전체 리뷰 갯수, 필터링 된 개뷰 갯수도 함께 반환해줍니다.

        Args:
            valid_param : validate_params에서 통과 한 QueryString.
            session : db connection 객체
        Returns:
            review_list : 글 번호, 셀러명, 상품명, 회원닉네임, 리뷰내용, 등록일시, 수정일시 return (r'type : dict)
            review_count : 전체 리뷰의 갯수, 필터링 된 리뷰의 갯수
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-07 (hj885353@gmail.com) : 초기 생성
            2020-10-12 (hj885353@gmail.com) : Pagination 로직 변경
             - SQL LIMIT, OFFSET 사용하여 10개씩 보기 등의 로직 가능하도록 구현
             - 마지막 페이지 number return 하도록 변경
            2020-10-13 (hj885353@gmail.com) : review_id 기준 내림차순 정렬 추가
        """
        # 리뷰에 필요한 데이터를 조회하는 쿼리문
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

        # 쿼리스트링이 들어왔을 때, 조건에 맞게 필터링 된 리뷰의 갯수를 count 해주는 쿼리문
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

        # pagination 및 내림차순 정렬
        if valid_param.get('filterLimit', None):
            if valid_param.get('page', None):
                valid_param['offset'] = valid_param['page'] * valid_param['filterLimit']
                select_review_statement += " ORDER BY r.id DESC LIMIT :filterLimit OFFSET :offset"
            else:
                select_review_statement += " ORDER BY r.id DESC LIMIT :filterLimit"

        # 리뷰 전체 가져와서 dict 형태로 casting
        review_lists = session.execute(select_review_statement, valid_param).fetchall()
        review_list = [ dict(review) for review in review_lists ]

        # 필터링 된 count를 fetch 및 dictionary로 casting
        review_count = int(session.execute(filter_query_values_count_statement, valid_param).fetchone()[0])

        page_number = math.ceil(review_count / valid_param['filterLimit'])

        return review_list, review_count, page_number

    def review_info(self, review_no, session):
        """
        리뷰 내용 보기 버튼 눌렀을 때, 모달창에 띄워지는 데이터를 반환해주는 함수

        path_parameter로 글 번호를 받아오고, 해당 글 번호에 맞는 데이터를 조회한 후 그 값을 리턴해줍니다.

        Args:
            review_no : validate_params에서 통과 한 path_parameter.
            session : db connection 객체
        Returns:
            review_info : 글 번호, 리뷰 내용 return (r'type : dict)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-08 (hj885353@gmail.com) : 초기 생성
        """
        # 인자로 받은 review_no를 새로운 dict 형태로 재정의
        review_no_data = {
            'review_no' : review_no['parameter_review_no']
        }

        # 조건을 충족하는 (인자로 받은 글 번호의) 회원 닉네임과 리뷰 내용을 조회하는 쿼리문
        review_info_statement = """
            SELECT
                u.login_id,
                r.content
            FROM reviews as r
            LEFT JOIN users as u ON r.user_id = u.id
            WHERE r.id = :review_no
            AND r.is_deleted = 0
            AND u.is_deleted = 0
        """

        # 쿼리문을 실행시킨 결과를 받아오고, tuple 형태이기 때문에 dict로 casting해온다.
        review_info = dict(session.execute(review_info_statement, review_no_data).fetchone())

        return review_info

    def delete_review(self, review_no, session):
        """
        리뷰 내용 삭제 API

        리뷰 삭제 버튼을 눌렀을 때, 해당 글 번호를 path_parameter로 받아 해당 글을 soft delete 처리한다.
        인자로 받은 글 번호에 해당하는 row를 찾아서 해당 row의 is_deleted 값을 1로 update 시킨다.

        Args:
            review_no : validate_params에서 통과 한 path_parameter.
            session : db connection 객체
        Returns:
            
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-08 (hj885353@gmail.com) : 초기 생성
        """
        # path_parameter로 받은 글 번호를 dict에 정의
        review_no_data = {
            'review_no' : review_no['parameter_review_no']
        }

        # is_deleted의 상태값을 변경시키는 쿼리문
        session.execute(("""
            UPDATE 
                reviews
            SET
                is_deleted = 1
            WHERE id = :review_no
            AND is_deleted = 0
            """), review_no_data)