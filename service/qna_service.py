class QnAService:
    def __init__(self, qna_dao):
        self.qna_dao = qna_dao

    def get_qna_list(self, valid_param, seller_info, session):
        """
        Q&A list를 보여주는 함수
        controller로부터 전달 받은 인자를 dao로 전달시켜주는 함수

        Args:
            valid_param : QueryString Validation을 통과 한 dict
            seller_info : seller_info를 담고 있음
            session : db connection 객체
        Returns:
            qna_list_result : 조건을 충족하는 Q&A 목록을 dao로부터 전달받아 controller로 return (r'type : tuple)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-05 (hj885353@gmail.com) : 초기 생성
        """
        qna_list_result = self.qna_dao.get_qna_list(valid_param, seller_info, session)
        return qna_list_result

    def qna_answer_info(self, valid_param, session):
        """
        Q&A list에서 답변하기 버튼 눌렀을 때, 해당 문의에 대한 info를 return해주는 API
        controller로부터 받은 인자를 dao로 전달 및 dao의 return값을 controller로 return

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
        qna_answer_result = self.qna_dao.qna_answer_info(valid_param, session)
        return qna_answer_result

    def insert_answer(self, valid_param, session):
        """
        문의 사항에 대해서 답변을 저장하는 API
        
        path_parameter와 답변 내용, 로그인 된 셀러에 대한 정보를 받아 dao의 함수로 전달해준다.

        Args:
            valid_param : 글 번호를 가리키는 PATH PARAMETER, 답변 내용인 answer, 답변 단 사람을 표시하기 위해 login한 seller_id를 가져옴
            session : db connection 객체
        Returns:
            SUCCESS, 200
            DB_ERROR, 500
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-06 (hj885353@gmail.com) : 초기 생성
        """
        self.qna_dao.insert_answer(valid_param, session)

    def delete_question(self, valid_param, session):
        """
        문의 사항에 대해서 답변을 삭제하는 API
        
        PUT method를 사용하여 is_deleted의 상태를 변경한다.
        인자로 전달 받은 값들을 dao의 함수로 전달해준다.

        Args:
            valid_param : 글 번호를 가리키는 PATH PARAMETER
            session : db connection 객체
        Returns:
            
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-06 (hj885353@gmail.com) : 초기 생성
        """
        self.qna_dao.delete_question(valid_param, session)