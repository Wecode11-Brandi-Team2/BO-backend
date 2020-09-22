from flask           import jsonify
from sqlalchemy.orm  import sessionmaker

class UserDao:
    """
    user table에서 필요한 field 조회 후 json 형태로 return
    """
    def get_user_info(self, session):
        # taransaction start
        try:
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

            return jsonify({'user_list' : [ dict(user) for user in users ]}) if users else None
        # error 발생 시 transaction rollbaock 처리
        except:
            session.rollback()
        # 실행 완료 후 transaction 종료