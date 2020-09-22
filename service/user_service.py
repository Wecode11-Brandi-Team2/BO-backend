class UserService:
    def __init__(self, user_dao):
        self.user_dao = user_dao

    def get_user_info_service(self):
        user_info = self.user_dao.get_user_info()
        
        return user_info