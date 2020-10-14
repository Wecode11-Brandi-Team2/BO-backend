import math

class UserDao:
    def get_user_info(self, valid_param, session):
        """
        Args:
            validate_param : validate_params를 통과 한 QueryString
            Session : db 연결
        Return:
            user_list : user에 대한 정보를 담은 list (r'type : list)
            total_user_number : Response로 보낼 데이터의 숫자 (r'type : int)
            page_number : 마지막 page_number (r'tpye : int)
        Authors:
            hj885353@gmail.com(김해준)
        History;
            2020-09-21 (hj885353@gmail.com) : 초기 생성
            2020-10-13 (hj885353@gmail.com)
            기존 : QueryString을 사용한 filtering 기능 없음
                controller에서 dict casting 후 return
            변경 : QueryString을 사용한 filtering 기능 추가
                dao에서 dict casting 한 후 그 값을 controller에서 받아서 return
        """
        select_user_statement = """
            SELECT
                id,
                login_id,
                phone_number,
                email,
                created_at
            FROM
                users
            WHERE is_deleted = 0
        """

        filter_query_values_count_statement = """
            SELECT
                count(0) as filtered_user_count
            FROM
                users
            WHERE is_deleted = 0
        """
        
        # 회원 번호
        if valid_param.get('mber_no', None):
            select_user_statement += " AND id = :mber_no"
            filter_query_values_count_statement += " AND id = :mber_no"

        # 회원 로그인 아이디
        if valid_param.get('mber_ncnm', None):
            select_user_statement += " AND login_id = :mber_ncnm"
            filter_query_values_count_statement += " AND login_id = :mber_ncnm"

        # 회원 핸드폰 번호
        if valid_param.get('mber_phone', None):
            select_user_statement += " AND phone_number = :mber_phone"
            filter_query_values_count_statement += " AND phone_number = :mber_phone"

        # 회원 이메일
        if valid_param.get('mber_email', None):
            select_user_statement += " AND email = :mber_email"
            filter_query_values_count_statement += " AND email = :mber_email"

        # 등록일시 ~부터 ~까지
        if valid_param.get('mber_date_from', None) and valid_param.get('mber_date_to', None):
            select_user_statement += " AND DATE(created_at) BETWEEN :mber_date_from AND :mber_date_to"
            filter_query_values_count_statement += " AND DATE(created_at) BETWEEN :mber_date_from AND :mber_date_to"

        # 페이지네이션
        if valid_param.get('filterLimit', None):
            if valid_param.get('page', None):
                valid_param['offset'] = (valid_param['page']-1) * valid_param['filterLimit']
                select_user_statement += " ORDER BY id DESC LIMIT :filterLimit OFFSET :offset"
            else:
                select_user_statement += " ORDER BY id DESC LIMIT :filterLimit"

        # 쿼리문을 만족하는 모든 user_list를 가져옴
        user_lists = session.execute(select_user_statement, valid_param).fetchall()
        user_list = [ dict(user) for user in user_lists ]

        # 쿼리문을 만족하는 raw의 갯수
        user_count = int(session.execute(filter_query_values_count_statement, valid_param).fetchone()[0])

        # 마지막 페이지 number를 넘겨줌. 올림 처리
        page_number = math.ceil(user_count / valid_param['filterLimit'])

        return user_list, user_count, page_number