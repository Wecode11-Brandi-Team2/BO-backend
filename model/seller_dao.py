import bcrypt
from flask           import jsonify
from sqlalchemy import text

class SellerDao:
    def insert_seller(self, seller_info, session):
        """
        seller 회원가입 시 입력 된 정보를 INSERT 하는 함수

        Args:
            seller_info:
                seller_loginID      : seller login ID,
                password            : seller 회원가입 시 비밀번호,
                korean_name         : 한글 이름,
                eng_name            : 영어 이름,
                service_center_phone: 서비스센터 전화번호,
                site_url            : 셀러 site_url,
                seller_id           : seller table FK로 연결되는 id
                seller_attribute_id : seller_attributes table FK로 연결되는 id
                seller_status_id    : seller_status table FK로 연결되는 id
                manager_id          : manager table FK로 연결되는 id
                modifier_id         : 수정 승인자에 대한 id
            session : db 연결
        Authors:
            hj885353@gmail.com(김해준)
        History:
            2020-09-23 (hj885353@gmail.com) : 초기 생성
            2020-09-24 (hj885353@gmail.com) : seller_id, manager_id, modifier_id가 연결되도록 수정
        """
        # sellers table에 data를 input
        seller_query = """
            INSERT INTO sellers (
                is_admin,
                created_at,
                is_deleted
            )VALUES """
        values = f"(0, now(), 0)"
        seller_query += values
        new_seller = session.execute(seller_query)
        # 새로 insert 되는 seller_id를 lastrowid를 사용하여 seller_info에 연결
        new_seller_last_id = new_seller.lastrowid

        # managers table에 data를 input
        manager_info_query = """
            INSERT INTO managers (
                phone_number,
                is_deleted             
            ) VALUES """
        values = f"({seller_info['phone_number']}, 0)"
        manager_info_query += values
        new_manager = session.execute(manager_info_query)
        # 새로 insert 되는 manager_id를 lastrowid를 사용하여 seller_info에 연결
        new_manager_last_id = new_manager.lastrowid

        # seller_info table에 data를 input
        seller_info_query = """
            INSERT INTO seller_info (
                seller_loginID,
                password, 
                korean_name,
                eng_name,
                service_center_phone,
                site_url,
                seller_id,
                seller_attribute_id,
                seller_status_id,
                manager_id,
                modifier_id,
                start_at,
                end_date,
                is_deleted
            ) VALUES """
        values = f"('{seller_info['seller_loginID']}', '{seller_info['hashed_password']}', '{seller_info['korean_name']}', '{seller_info['eng_name']}', '{seller_info['center_number']}' , '{seller_info['site_url']}', {new_seller_last_id}, {seller_info['attribute_id']}, 1, {new_manager_last_id}, {new_seller_last_id}, now(), '9999-12-31 23:59:59', 0)"
        seller_info_query += values
        seller_info = session.execute(seller_info_query)

    def get_seller_id_and_password(self, seller_info, session):
        """
        로그인 하기 위해 seller의 id와 password를 select 하는 함수

        Args:
            loginID : dict 형태의 input으로 들어오는 loginID
            session : db 연결
        Return:
            {
                'seller_loginID': 'testid1', 
                'password': '$2b$12$x5Povw7bxtOFKT10c5eXzeghAOjuMS2RW9WL5XLo7v.5CapKjAeNS'
            }
        Authors:
            hj885353@gmail.com(김해준)
        History:
            2020-09-25 (hj885353@gmail.com) : 초기 생성
        """
        # request로 들어 온 ID에 해당하는 password를 가지고 와서 fetch. return type : tuple
        seller_info_statement = """
            SELECT
                sellers.id,
                password
            FROM
                seller_info
            LEFT OUTER JOIN sellers ON sellers.id = seller_info.seller_id
            WHERE
                seller_loginID = :login_id
        """
        seller = session.execute(seller_info_statement, seller_info).fetchone()
        # tuple -> dictionary로 casting해서 return
        return dict(seller)

    def get_seller_list(self, valid_param, session):
        """ 셀러 리스트를 표출 및 검색 기능 GET 함수.
        pagination: offset 과 limit 값을 받아 pagination 구현
        filtering: 키워드를 받아서 검색기능 구현

        Args:
            valid_param: controller에서 valid param을 통과 한 parameter
            session : db connection 객체
        Returns: 
            seller_info: seller infomation return (r'type : list)
            seller_count: seller 전체 갯수, filtering되면 filtering 된 seller의 갯수 return (r'type : dict)
        Authors:
            hj885353@gmail.com(김해준)
        History:
            2020-09-28(hj885353@gmail.com): 초기 생성
        """
        # 키워드 검색을 위한 쿼리문
        select_seller_list_statement = """
            SELECT
                seller_info.seller_id,
                seller_loginID,
                eng_name,
                korean_name,
                managers.name,
                seller_status_id,
                managers.phone_number,
                managers.email,
                seller_attribute_id,
                (
                    SELECT COUNT(DISTINCT product_info.product_id)
                    FROM product_info
                    WHERE product_info.seller_id = sellers.id
                ) as product_count,
                site_url,
                start_at
            FROM seller_info
            JOIN sellers ON sellers.id = seller_info.seller_id
            JOIN managers ON managers.id = seller_info.manager_id
            WHERE seller_info.end_date = '9999-12-31 23:59:59'
            AND seller_info.is_deleted = 0
            AND sellers.is_deleted = 0
            AND managers.is_deleted = 0
        """
        
        # 키워드검색이 들어왔을 때 검색결과의 셀러를 count 하기 위한 쿼리
        filter_query_values_count_statement = """
            SELECT 
                COUNT(0) as filtered_seller_count
            FROM seller_info
            JOIN sellers ON sellers.id = seller_info.seller_id
            JOIN managers ON managers.id = seller_info.manager_id
            WHERE seller_info.end_date = '9999-12-31 23:59:59'
            AND seller_info.is_deleted = 0
            AND sellers.is_deleted = 0
        """

        # 회원 번호
        if valid_param.get('mber_no', None):
            select_seller_list_statement += " AND seller_id = :mber_no"
            filter_query_values_count_statement += " AND seller_id = :mber_no"

        # 셀러 아이디
        if valid_param.get('mber_ncnm', None):
            select_seller_list_statement += " AND seller_loginID = :mber_ncnm"
            filter_query_values_count_statement += " AND seller_loginID = : mber_ncnm"

        # 영어 이름
        if valid_param.get('mber_en', None):
            select_seller_list_statement += " AND eng_name = :mber_en"
            filter_query_values_count_statement += " AND eng_name = :mber_en"

        # 한글 이름
        if valid_param.get('mber_ko', None):
            select_seller_list_statement += " AND korean_name = :mber_ko"
            filter_query_values_count_statement += " AND korean_name = :mber_ko"

        # 담당자 이름
        if valid_param.get('manager_name', None):
            select_seller_list_statement += " AND managers.name = :manager_name"
            filter_query_values_count_statement += " AND managers.name = :manager_name"

        # 셀러 상태
        if valid_param.get('seller_status', None):
            select_seller_list_statement += " AND seller_status_id = :seller_status"
            filter_query_values_count_statement += " AND seller_status_id = :seller_status"

        # 담당자 연락처
        if valid_param.get('manager_telno', None):
            select_seller_list_statement += " AND managers.phone_number = :manager_telno"
            filter_query_values_count_statement += " AND managers.phone_number = :manager_telno"

        # 담당자 이메일
        if valid_param.get('manager_email', None):
            select_seller_list_statement += " AND managers.email = :manager_email"
            filter_query_values_count_statement += " AND managers.email = :manager_email"

        # 셀러 속성
        if valid_param.get('seller_attribute', None):
            select_seller_list_statement += " AND seller_attribute_id = :seller_attribute"
            filter_query_values_count_statement += " AND seller_attribute_id = :seller_attribute"

        # 등록일 검색 시작 날짜
        if valid_param.get('mber_date_from', None):
            select_seller_list_statement += " AND DATE(start_at) = :mber_date_from"
            filter_query_values_count_statement += " AND DATE(start_at) = :mber_date_from"

        # 등록일 검색 끝 날짜
        if valid_param.get('mber_date_from', None) and valid_param.get('mber_date_to', None):
            select_seller_list_statement += " AND DATE(start_at) BETWEEN :mber_date_from AND :mber_date_to"
            filter_query_values_count_statement += " AND DATE(start_at) BETWEEN :mber_date_from AND :mber_date_to"

        # action
        if valid_param.get('action', None):
            select_seller_list_statement += " AND action = :action"
            filter_query_values_count_statement += " AND action = :action"

        # 선분이력 시작
        if valid_param.get('start_at', None):
            select_seller_list_statement += " AND start_at = :start_at"
            filter_query_values_count_statement += " AND start_at = :start_at"

        # 선분이력 끝
        if valid_param.get('end_date', None):
            select_seller_list_statement += " AND end_date = :end_date"
            filter_query_values_count_statement += " AND end_date = :end_date"
        
        # sql 명령문에 키워드 추가가 완료되면 정렬, limit, offset 쿼리문 추가
        select_seller_list_statement += " ORDER BY seller_info.seller_id DESC LIMIT :limit OFFSET :offset"
        seller_infos = session.execute(select_seller_list_statement, valid_param).fetchall()
        seller_info = [ dict(seller) for seller in seller_infos ]
        
        # pagination 을 위해서 전체 셀러가 몇명인지 count 해서 기존의 seller_info 에 넣어줌.
        seller_count_statement = """
            SELECT
                COUNT(seller_id) as total_seller_count
            FROM seller_info
            LEFT JOIN sellers ON seller_info.seller_id = sellers.id 
            WHERE end_date = '9999-12-31 23:59:59' AND sellers.is_deleted = 0
        """
        seller_count = dict(session.execute(seller_count_statement).fetchone())

        # 쿼리파라미터가 들어오면 필터 된 셀러를 카운트하고 리턴 값에 포함시킨다. 쿼리파라미터가 들어오지않으면 전체 셀러 수를 포함시킴.
        filter_query_values_count = dict(session.execute(filter_query_values_count_statement, valid_param).fetchone())

        seller_count['filtered_seller_count'] = filter_query_values_count['filtered_seller_count']
        return seller_info, seller_count