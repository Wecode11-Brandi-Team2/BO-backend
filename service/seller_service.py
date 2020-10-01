import bcrypt
import jwt

from config import SECRET

class SellerService:
    def __init__(self, seller_dao):
        self.seller_dao = seller_dao

    def create_new_seller(self, seller_info, session):
        """
        seller 회원가입 시 입력 받은 password를 hash화 하는 함수

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
        """
        seller_info['hashed_password'] = bcrypt.hashpw(
            seller_info['password'].encode('UTF-8'),
            bcrypt.gensalt()
        ).decode('UTF-8')
        self.seller_dao.insert_seller(seller_info, session)

    def login(self, seller_info, session):
        """
        input으로 들어 온 loginID에 해당하는 password와 DB에 저장 된 password를 비교하는 함수

        Args:
            credential : request.json
            session : db 연결
        Return:
            비교 시 일치 : True
            비교 시 불일치 : False
        Authors:
            hj885353@gmail.com(김해준)
        History:
            2020-09-25 (hj885353@gmail.com) : 초기 생성
        """
        seller_credential = self.seller_dao.get_seller_id_and_password(seller_info, session)
        authorized = bcrypt.checkpw(seller_info['password'].encode('UTF-8'), seller_credential['password'].encode('UTF-8'))
        return authorized

    def get_seller_id_and_password(self, seller_info, session):
        """
        DB에서 dict 형태의 loginID와 hash화 된 password를 controller와 연결시켜주는 함수

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
        """
        return self.seller_dao.get_seller_id_and_password(seller_info, session)

    def generate_access_token(self, seller_info, session):
        """
        input으로 들어온 ID와 password가 일치했을 경우 token을 발행해주는 함수

        Args:
            loginID : loginID
            session : db 연결
        Return:
            access_token
        Authors:
            hj885353@gmail.com(김해준)
        History:
            2020-09-25 (hj885353@gmail.com) : 초기 생성
        """
        seller_info_result = self.seller_dao.get_seller_id_and_password(seller_info, session)
        access_token = jwt.encode({'seller_no' : seller_info_result['id']}, SECRET['SECRET_KEY'], algorithm = SECRET['ALGORITHMS']).decode('UTF-8')
        return access_token

    def get_seller_list(self, valid_param, seller_no, session):
        """ 가입된 모든 셀러 정보 리스트 표출
        dao에서 받아 온 값을 controller로 return해주는 함수
        Args:
            valid_param: 클라이언트에서 온 요청
            loginID: seller_login_ID
            session: db connection 객체
        Returns:
            seller_list_result: 셀러 정보 리스트 (r'type : tuple)
        Authors:
            hj885353@gmail.com
        History:
            2020-09-28 (hj885353@gmail.com): 초기 생성
        """
        seller_list_result = self.seller_dao.get_seller_list(valid_param, session)
        return seller_list_result

    def get_seller_info(self, seller_info, session):
        """ 계정의 셀러정보 표출
        controller에서 받은 seller_info를 dao의 get_seller_info 함수로 전달

        Args:
            seller_info: seller 정보
            session: db connection 객체
        Returns:
            seller_info_result (r'type : dict)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-09-30 (hj885353@gmail.com) : 초기 생성
        """
        seller_info_result = self.seller_dao.get_seller_info(seller_info, session)

        return seller_info_result

    def change_seller_info(self, seller_info_data, session):
        """
        endpoint로부터 전달 받은 seller에 대한 data를 dao로 전달시키는 함수입니다.

        Args:
            seller_info_data: endpoint에서 전달받은 seller에 대한 정보
            session: db connection 객체
        Returns:

        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-01 (hj885353@gmail.com) : 초기 생성
        """
        change_seller_info_result = self.seller_dao.change_seller_info(seller_info_data, session)