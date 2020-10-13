class UserService:
    def __init__(self, user_dao):
        self.user_dao = user_dao

    def get_user_info_service(self, valid_param, session):
        """
        Args:
            validate_param : validate_params를 통과 한 QueryString
            Session : db 연결
        Return:
            user_info : user_list, user_count, page_number를 담고 있는 변수 (r'type : tuple)
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
        user_info = self.user_dao.get_user_info(valid_param, session)
        
        return user_info