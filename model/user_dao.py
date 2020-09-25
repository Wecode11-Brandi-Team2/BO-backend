class UserDao:
    """
    user table에서 필요한 field 조회 후 json 형태로 return
    """
    def get_user_info(self, session):
        users = session.execute(
            """
            SELECT
                id,
                login_id,
                phone_number,
                email,
                created_at
            FROM
                users
            """).fetchall()

        return users