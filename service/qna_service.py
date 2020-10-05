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