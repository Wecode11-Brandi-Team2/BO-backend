import bcrypt
import datetime
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
            2020-10-07 (hj885353@gmail.com) : schema 변경으로 쿼리문 수정
                기존 : seller_info Table -> loginID
                변경 : sellers Table -> login_id
        """
        # sellers table에 data를 input
        seller_query = """
            INSERT INTO sellers (
                login_id,
                is_admin,
                created_at,
                is_deleted
            )VALUES """
        values = f"('{seller_info['seller_loginID']}', 0, now(), 0)"
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
        values = f"('{seller_info['hashed_password']}', '{seller_info['korean_name']}', '{seller_info['eng_name']}', '{seller_info['center_number']}' , '{seller_info['site_url']}', {new_seller_last_id}, {seller_info['attribute_id']}, 1, {new_manager_last_id}, {new_seller_last_id}, now(), '9999-12-31 23:59:59', 0)"
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
            2020-10-07 (hj885353@gmail.com) : schema 변경으로 쿼리문 수정
                기존 : seller_info Table -> loginID
                변경 : sellers Table -> login_id
        """
        # request로 들어 온 ID에 해당하는 password를 가지고 와서 fetch. return type : tuple
        seller_info_statement = """
            SELECT
                sellers.id,
                password
            FROM
                seller_info
            LEFT OUTER JOIN sellers ON sellers.id = seller_info.seller_id
            WHERE sellers.login_id = :login_id
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
            2020-10-07 (hj885353@gmail.com) : schema 변경으로 쿼리문 수정
                기존 : seller_info Table -> loginID
                변경 : sellers Table -> login_id
        """
        # 키워드 검색을 위한 쿼리문
        select_seller_list_statement = """
            SELECT
                seller_info.seller_id,
                sellers.login_id,
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
            select_seller_list_statement += " AND sellers.login_id = :mber_ncnm"
            filter_query_values_count_statement += " AND sellers.login_id = :mber_ncnm"

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

    def get_seller_info(self, seller_info, session):
        """ 계정의 셀러정보 표출
        seller_info['parameter_seller_no']로 seller_no를 인자로 받아 해당 seller의 정보 표출

        Args:
            seller_info: seller 정보
            (parameter_seller_no: path parameter로 받은 seller의 no)
            session: db connection 객체
        Returns:
            seller_info_result (r'type : dict)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-09-30 (hj885353@gmail.com) : 초기 생성
        """
        # 인자로 받은 seller_info에섯 seller_no를 미리 정의하기 위한 dict
        # 해당 작업을 수행하지 않을 경우 python dict cannot converted Error 발생
        seller_no_data = {
            'seller_no' : seller_info['parameter_seller_no']
        }
        # seller_info로 넘어 온 id 값을 가진 seller의 정보를 표출해 주는 쿼리문
        seller_info_statement = """
            SELECT
                image_url,
                seller_status_id,
                seller_attribute_id,
                korean_name,
                eng_name,
                s.login_id,
                seller_page_background_image_url,
                simple_description,
                detail_description,
                m.name,
                m.phone_number,
                m.email,
                service_center_phone,
                postal_code,
                address,
                service_center_open_time,
                service_center_close_time,
                bank,
                account_holder,
                account_number,
                start_at,
                end_date,
                modifier_id,
                shipping_info,
                refund_policy,
                model_height,
                model_top_size,
                model_pants_size,
                model_foots_size,
                update_feed_message
            FROM seller_info as si
            INNER JOIN sellers as s ON s.id = si.seller_id
            INNER JOIN managers as m ON m.id = si.manager_id
            INNER JOIN seller_status as ss ON ss.id = si.seller_status_id
            INNER JOIN seller_attributes as sa ON sa.id = si.seller_attribute_id
            WHERE si.end_date = '9999-12-31 23:59:59'
            AND s.id = :seller_no
            AND si.is_deleted = 0
            AND s.is_deleted = 0
            AND m.is_deleted = 0
        """
        # tuple -> dict로 casting
        seller_info_result = dict(session.execute(seller_info_statement, seller_no_data).fetchone())

        return seller_info_result

    def change_seller_info(self, seller_info_data, session):
        """
        셀러의 수정 정보를 INSERT 하는 함수입니다.
        셀러의 정보는 선분이력으로 관리하기 때문에 INSERT INTO 를 사용하였습니다.

        새로운 DB의 정보가 들어오면, 기존의 데이터를 삭제 처리 (soft delete) 및 종료 시간을 업데이트 해 주고,
        새로 INSERT 된 raw의 시간과 일치하도록 하여 하나의 선분이 되도록 구성하였습니다.

        Args:
            seller_info_data: endpoint에서 전달받은 seller에 대한 정보
            session: db connection 객체
        Returns:

        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-01 (hj885353@gmail.com) : 초기 생성
            2020-10-07 (hj885353@gmail.com)
                기존 : now()를 바로 사용
                변경 : db에서 now()를 미리 조회 한 후 해당 값을 변수에 할당하여 그 값을 INSERT 및 UPDATE로 선분이력 관리되도록 변경
                    : 새로운 row INSERT 시 password가 INSERT 되지 않아 해당 부분 수정
        """
        # 선분이력에 사용 할 now를 db에서 조회
        now = session.execute("""
            SELECT
                now()            
        """).fetchone()

        # 인자로 받은 seller_info_data의 값을 가지고 와서 db에 넣어주기 위한 작업
        seller_info = {
              'image_url'                       : seller_info_data['seller_data']['image_url'],
              'seller_no'                       : seller_info_data['parameter_seller_no'],
              'seller_status_id'                : seller_info_data['seller_data']['seller_status_id'],
              'seller_attribute_id'             : seller_info_data['seller_data']['seller_attribute_id'],
              'manager_id'                      : seller_info_data['seller_info']['manager_id'],
              'korean_name'                     : seller_info_data['seller_data']['korean_name'],
              'eng_name'                        : seller_info_data['seller_data']['eng_name'],
              'seller_page_background_image_url': seller_info_data['seller_data']['seller_page_background_image_url'],
              'simple_description'              : seller_info_data['seller_data']['simple_description'],
              'detail_description'              : seller_info_data['seller_data']['detail_description'],
              'service_center_phone'            : seller_info_data['seller_data']['service_center_phone'],
              'postal_code'                     : seller_info_data['seller_data']['postal_code'],
              'address'                         : seller_info_data['seller_data']['address'],
              'service_center_open_time'        : seller_info_data['seller_data']['service_center_open_time'],
              'service_center_close_time'       : seller_info_data['seller_data']['service_center_close_time'],
              'bank'                            : seller_info_data['seller_data']['bank'],
              'account_holder'                  : seller_info_data['seller_data']['account_holder'],
              'account_number'                  : seller_info_data['seller_data']['account_number'],
              'modifier_id'                     : seller_info_data['seller_data']['modifier_id'],
              'shipping_info'                   : seller_info_data['seller_data']['shipping_info'],
              'refund_policy'                   : seller_info_data['seller_data']['refund_policy'],
              'model_height'                    : seller_info_data['seller_data']['model_height'],
              'model_top_size'                  : seller_info_data['seller_data']['model_top_size'],
              'model_pants_size'                : seller_info_data['seller_data']['model_pants_size'],
              'model_foots_size'                : seller_info_data['seller_data']['model_foots_size'],
              'update_feed_message'             : seller_info_data['seller_data']['update_feed_message']
        }

        password = session.execute(("""
            SELECT
                password
            FROM seller_info
            WHERE seller_id = :seller_no
            AND is_deleted = 0
        """), seller_info).fetchone()

        # db에서 조회한 ResultProxy를 dict에 추가시켜줌
        seller_info['now'] = now['now()']
        seller_info['password'] = password['password']

        # 삭제여부, 선분이력 종료시간에 대한 정보를 업데이트 할 쿼리문
        session.execute(("""
            UPDATE
                seller_info
            SET
                is_deleted = 1,
                end_date = :now
            WHERE seller_id = :seller_no
            AND is_deleted = 0
            """), seller_info)

        # arguments로 들어온 새로운 seller 정보 중 seller_info table에 INSERT 할 쿼리문
        session.execute(("""
            INSERT INTO seller_info (
                image_url,
                seller_id,
                seller_status_id,
                seller_attribute_id,
                manager_id,
                korean_name,
                eng_name,
                password,
                seller_page_background_image_url,
                simple_description,
                detail_description,
                service_center_phone,
                postal_code,
                address,
                service_center_open_time,
                service_center_close_time,
                bank,
                account_holder,
                account_number,
                modifier_id,
                shipping_info,
                refund_policy,
                model_height,
                model_top_size,
                model_pants_size,
                model_foots_size,
                update_feed_message,
                start_at,
                end_date,
                is_deleted
            ) VALUES (
                :image_url,
                :seller_no,
                :seller_status_id,
                :seller_attribute_id,
                :manager_id,
                :korean_name,
                :eng_name,
                :password,
                :seller_page_background_image_url,
                :simple_description,
                :detail_description,
                :service_center_phone,
                :postal_code,
                :address,
                :service_center_open_time,
                :service_center_close_time,
                :bank,
                :account_holder,
                :account_number,
                :modifier_id,
                :shipping_info,
                :refund_policy,
                :model_height,
                :model_top_size,
                :model_pants_size,
                :model_foots_size,
                :update_feed_message,
                :now,
                '9999-12-31 23:59:59',
                0
            )"""), seller_info)

        # 인자로 받은 seller_info_data의 값을 가지고 와서 db에 넣어주기 위한 작업
        manager_info = {
            'manager_name'        : seller_info_data['seller_data']['manager_name'],
            'manager_phone_number': seller_info_data['seller_data']['manager_phone_number'],
            'manager_email'       : seller_info_data['seller_data']['manager_email']
        }

        # arguments로 들어온 새로운 seller 정보 중 managers table에 INSERT 할 쿼리문
        session.execute(("""
            INSERT INTO managers (
                name,
                phone_number,
                email
            ) VALUES (
                :manager_name,
                :manager_phone_number,
                :manager_email
            )"""), manager_info)

    def check_duplication_kor(self, kor_name, session):
        """
        셀러 정보 수정에서 한글 셀러명에 대한 중복검사를 하기 위해 DB에서 한글 셀러명을 조회하는 함수

        Args:
            kor_name : request로부터 받아 온 사용자가 입력 한 한글 셀러명
            session: db connection 객체
        Returns:
            seller_kor_name: DB에서 가져온 일치하는 한글 셀러명의 갯수(r'type : int)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-02 (hj885353@gmail.com) : 초기 생성
            2020-10-07 (hj885353@gmail.com)
                기존 : DB의 한글 셀러명을 모두 다 가져와서 list에 append 후 존재하는지 look up 하는 로직
                변경 : DB에 request로 넘어온 한글 셀러명이 존재하는지 count로 확인. 존재하는 경우 count = 1, 존재하지 않는 경우 count = 0. 이걸로 판별하도록 변경
        """
        # DB에 있는 한글 셀러명 중 인자로 넘어온 kor_name이 있는지 조회하는 쿼리문
        seller_kor_name_statement = """
            SELECT
                korean_name
            FROM seller_info
            WHERE korean_name = :korean_name 
            AND is_deleted = 0
        """
        # rowcount로 일치하는 한글 셀러명의 수를 count한다. 있을 경우 1, 없을 경우 0
        seller_kor_name = session.execute(seller_kor_name_statement, kor_name).rowcount
        return seller_kor_name

    def check_duplication_eng(self, eng_name, session):
        """
        셀러 정보 수정에서 영문 셀러명에 대한 중복검사를 하기 위해 DB에서 영문 셀러명을 조회하는 함수

        Args:
            eng_name : request로부터 받아 온 사용자가 입력 한 영문 셀러명
            session: db connection 객체
        Returns:
            seller_eng_name: DB에서 가져온 일치하는 영문 셀러명의 갯수(r'type : int)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-02 (hj885353@gmail.com) : 초기 생성
            2020-10-07 (hj885353@gmail.com)
                기존 : DB의 영문 셀러명을 모두 다 가져와서 list에 append 후 존재하는지 look up 하는 로직
                변경 : DB에 request로 넘어온 영문 셀러명이 존재하는지 count로 확인. 존재하는 경우 count = 1, 존재하지 않는 경우 count = 0. 이걸로 판별하도록 변경
        """
        # DB에 있는 한글 셀러명 중 인자로 넘어온 eng_name이 있는지 조회하는 쿼리문
        seller_eng_name_statement = """
            SELECT
                eng_name
            FROM seller_info
            WHERE eng_name = :eng_name
            AND is_deleted = 0
        """
        # rowcount로 일치하는 영문 셀러명의 수를 count한다. 있을 경우 1, 없을 경우 0
        seller_eng_name = session.execute(seller_eng_name_statement, eng_name).rowcount
        return seller_eng_name

    def get_password(self, change_info, session):
        seller_no_data = {
            'seller_no' : change_info['seller_info']['seller_no']
        }
        
        seller_password_statement = """
            SELECT
                password
            FROM seller_info
            WHERE is_deleted = 0
            AND seller_id = :seller_no
        """
        origin_password = dict(session.execute(seller_password_statement, seller_no_data).fetchone())

        return origin_password

    def change_password(self, change_info, hashed_password, session):
        change_info_data = {
            'password' : hashed_password,
            'seller_no': change_info['seller_info']['seller_no']
        }

        update_password_statement = """
            UPDATE
                seller_info
            SET 
                password = :password
            WHERE seller_id = :seller_no
            AND is_deleted = 0
        """

        session.execute(update_password_statement, change_info_data)