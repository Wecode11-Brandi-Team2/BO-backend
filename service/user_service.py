class UserService:
    def __init__(self, user_dao):
        self.user_dao = user_dao

    def get_user_info_service(self, session):
        user_info = self.user_dao.get_user_info(session)
        
        return user_info