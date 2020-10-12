import bcrypt
import jwt

from flask import jsonify

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

    def check_duplication_kor(self, kor_name, session):
        """
        셀러 정보 수정 관리 중 한글 셀러명을 변경할 때 셀러명에 대한 중복 검사를 실시하는 함수
        controller와 dao를 연결시켜주는 함수

        Args:
            kor_name : request로부터 받아 온 사용자가 입력한 한글 셀러명
            session: db connection 객체
        Returns:
            check_duplication_result: DB에서 가져온 일치하는 한글 셀러명의 갯수(r'type : int)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-02 (hj885353@gmail.com) : 초기 생성
            2020-10-07 (hj885353@gmail.com)
                기존 : DB의 한글 셀러명을 모두 다 가져와서 list에 append 후 존재하는지 look up 하는 로직
                변경 : DB에 request로 넘어온 한글 셀러명이 존재하는지 count로 확인. 존재하는 경우 count = 1, 존재하지 않는 경우 count = 0. 이걸로 판별하도록 변경
        """
        check_duplication_result = self.seller_dao.check_duplication_kor(kor_name, session)

        return check_duplication_result

    def check_duplication_eng(self, eng_name, session):
        """
        셀러 정보 수정 관리 중 영문 셀러명을 변경할 때 셀러명에 대한 중복 검사를 실시하는 함수
        controller와 dao를 연결시켜주는 함수

        Args:
            eng_name : request로부터 받아 온 사용자가 입력한 영문 셀러명
            session: db connection 객체
        Returns:
            check_duplication_result: DB에서 가져온 일치하는 영문 셀러명의 갯수(r'type : int)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-02 (hj885353@gmail.com) : 초기 생성
            2020-10-07 (hj885353@gmail.com)
                기존 : DB의 영문 셀러명을 모두 다 가져와서 list에 append 후 존재하는지 look up 하는 로직
                변경 : DB에 request로 넘어온 영문 셀러명이 존재하는지 count로 확인. 존재하는 경우 count = 1, 존재하지 않는 경우 count = 0. 이걸로 판별하도록 변경
        """
        check_duplication_result = self.seller_dao.check_duplication_eng(eng_name, session)

        return check_duplication_result

    def change_password(self, change_info, session):
        """
        셀러 정보 수정 중 패스워드 변경 함수

        Args:
            change_info : 사용자가 입력한 현재 패스워드, 수정 할 패스워드, 로그인 데코레이터를 통과 한 seller 정보
            session : db connection 객체
        Returns:
            change_password_result : 현재 비밀번호와 DB에 저장되어 있는 비밀번호를 비교 (r'type : boolean)
            confirm_password_result : 수정하려는 비밀번호와 DB에 저장되어 있는 비밀번호를 비교 (r'type : boolean)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-02 (hj885353@gmail.com) : 초기 생성
            2020-10-12 (hj885353@gmail.com)
                기존 : 비밀번호 수정만 가능. 수정이 성공적으로 이루어지는 경우 외 다른 경우에 대한 로직이 없었음
                변경 : 기존과 동일한 비밀번호를 입력한 경우와 비밀번호가 다른 경우에 대한 로직 추가
        """
        # DB에서 기존의 비밀번호를 가져옴
        origin_password = self.seller_dao.get_password(change_info, session)
        # 현재 비밀번호와 DB에서 가져온 기존의 비밀번호를 비교
        change_password_result = bcrypt.checkpw(change_info['original_password'].encode('UTF-8'), origin_password['password'].encode('UTF-8'))
        # 수정하려는 비밀번호와 DB에서 가져온 기존의 비밀번호를 비교
        confirm_password_result = bcrypt.checkpw(change_info['new_password'].encode('UTF-8'), origin_password['password'].encode('UTF-8'))
        
        # 현재 비밀번호와 DB 비밀번호가 같을 경우
        if change_password_result:

            # 수정하려는 비밀번호와 DB 저장되어 있는 비밀번호가 같지 않은 경우
            if not confirm_password_result:
                # 새로운 비밀번호를 hash화하여 dao에 전달
                hashed_password = bcrypt.hashpw(change_info['new_password'].encode('UTF-8'), bcrypt.gensalt()).decode('UTF-8')
                self.seller_dao.change_password(change_info, hashed_password, session)
                # 두개의 boolean값을 controller에 return
                return change_password_result, confirm_password_result

            return change_password_result, confirm_password_result
        # 현재 비밀번호와 DB의 비밀번호부타가 다른 경우는 하위의 boolean만 controller로 전달
        return change_password_result