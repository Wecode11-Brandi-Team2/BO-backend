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

    def qna_answer_info(self, valid_param, session):
        """
        Q&A list에서 답변하기 버튼 눌렀을 때, 해당 문의에 대한 info를 return해주는 API
        valid_param 인자로부터 글 번호를 받아 해당 글 번호에 관련 된 정보를 조회하여 dict 형태로 return해준다.

        Args:
            valid_param : validate_params에서 통과 한 QueryString. 글 번호를 받아서 해당 글 번호에 대한 info를 return
            session : db connection 객체
        Returns:
            qna_answer_result : 해당 글 번호에 해당하는 글 번호, 문의 유형, 닉네임, 상품명, 상품 이미지, 문의 내용, 문의 생성 시간을 return (r'type : dict)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-06 (hj885353@gmail.com) : 초기 생성
            2020-10-06 (hj885353@gmail.com) : QueryString을 path_parameter로 수정
        """
        
        # 해당 문의 내용에 대한 내용을 조회하는 쿼리문
        answer_info_statement = """
            SELECT
                q.id,
                qt.type_name,
                u.login_id,
                pi.name,
                pi.main_img,
                q.content,
                q.created_at
            FROM questions as q
            LEFT JOIN question_types as qt ON qt.id = q.type_id
            LEFT JOIN users as u ON u.id = q.user_id
            LEFT JOIN products as p ON p.id = q.product_id
            LEFT JOIN product_info as pi ON pi.product_id = p.id
            WHERE q.id = :parameter_question_no
            AND q.is_deleted = 0
            AND u.is_deleted = 0
            AND p.is_deleted = 0
            AND pi.is_deleted = 0
        """
        # 조회한 쿼리문을 fetch 및 dict로 casting
        answer_info = dict(session.execute(answer_info_statement, valid_param).fetchone())

        return answer_info        

    def insert_answer(self, valid_param, session):
        """
        문의 사항에 대해서 답변을 저장하는 API
        
        path_parameter로 문의 글 번호를 받아 해당 글에 대한 답변으로 저장
        답변이 저장되면 questions table의 답변 여부인 is_answered = 1로 UPDATE

        Args:
            valid_param : 글 번호를 가리키는 PATH PARAMETER, 답변 내용인 answer, 답변 단 사람을 표시하기 위해 login한 seller_id를 가져옴
            session : db connection 객체
        Returns:
            
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-06 (hj885353@gmail.com) : 초기 생성
        """
        # 인자로 받은 valid_param은 bind 되어 있기 때문에 한번 unpacking 해 준다.
        answer_info = {
            'question_id': valid_param['parameter_question_no'],
            'replier_id' : valid_param['seller_info']['seller_no'],
            'answer'     : valid_param['answer']
        }
        # answers table에 답변 정보를 저장
        session.execute(("""
            INSERT INTO answers (
                id,
                replier_id,
                content,
                created_at,
                is_deleted                
            ) VALUES (
                :question_id,
                :replier_id,
                :answer,
                now(),
                0
            )"""), answer_info)

        # 답변이 달렸기 때문에 questions table의 답변 여부를 가르키는 is_answered = 1로 update
        session.execute(("""
            UPDATE
                questions
            SET
                is_answered = 1
            WHERE id = :question_id
            AND is_answered = 0
            AND is_deleted = 0
            """), answer_info)

    def delete_question(self, valid_param, session):
        """
        문의 사항에 대해서 답변을 삭제하는 API
        
        PUT method를 사용하여 is_deleted의 상태를 변경한다.
        실제 데이터를 삭제하지는 않고, is_deleted = 1로 상태를 변경하여 삭제 된 것으로 처리하는 soft_delete 사용
        해당 문의 사항에 대한 답변이 달려있는지 조건 판별 후 문의 사항이 지워질 때 답변도 soft delete 처리

        Args:
            valid_param : 글 번호를 가리키는 PATH PARAMETER
            session : db connection 객체
        Returns:
            
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-06 (hj885353@gmail.com) : 초기 생성
        """
        # 인자로 받은 valid_param을 dict로 unpacking
        delete_info = {
            'question_id' : valid_param['parameter_question_no']
        }

        # is_deleted의 상태를 변경하는 쿼리문
        session.execute(("""
            UPDATE 
                questions
            SET
                is_deleted = 1
            WHERE id = :question_id
            AND is_deleted = 0
            """), delete_info)

        # questions Table에서 답변 여부를 조회하기 위한 쿼리문
        question_answered_statement = """
            SELECT
                q.is_answered
            FROM questions as q
            WHERE q.id = :question_id
        """
        is_answered = dict(session.execute(question_answered_statement, delete_info).fetchone())
        
        # 조회 했을 때, 답변의 상태가 1인 경우 answers Table에서도 is_deleted = 1로 상태 변경 ( 답변이 달려 있는 경우 )
        if is_answered['is_answered'] == 1:
            session.execute(("""
                UPDATE
                    answers
                SET
                    is_deleted = 1
                WHERE id = :question_id
                AND is_deleted = 0
                """), delete_info)