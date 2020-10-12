class CouponService:
    def __init__(self, coupon_dao):
        self.coupon_dao = coupon_dao

    def get_coupon_count(self, select_condition, session):
        """
        전체 쿠폰 갯수 조회 비즈니스 로직
            전체 쿠폰 갯수를 조회하는 DAO 메소드의 결과값을 controller에게 전달합니다. 
        args :
            session : connection 형성된 session 객체

        returns :
            전체 쿠폰 갯수

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-09 (이용민) : 초기 생성
        """

        total_coupon_num = self.coupon_dao.select_coupon_count(select_condition, session)
        return total_coupon_num

    def get_coupon_list(self, select_condition, session):
        """
        쿠폰리스트 조회 비즈니스 로직
            쿠폰조회 DAO 메소드에서 전달받은 결과값을 controller에게 전달합니다.

        args :
            page    : 페이지네이션 
            session : connection 형성된 session 객체

        returns :
            쿠폰정보 리스트 

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-06 (이용민) : 초기 생성
        """

        coupon_list = self.coupon_dao.select_coupons(select_condition, session)

        res_coupon_list = []
        for coupon_info in coupon_list:
            dict_coupon_info = dict(coupon_info)
            dict_coupon_info['validation_start_date'] = dict_coupon_info['validation_start_date'].strftime('%Y-%m-%d %H:%M')
            dict_coupon_info['validation_end_date'] = dict_coupon_info['validation_end_date'].strftime('%Y-%m-%d %H:%M')
            dict_coupon_info['download_start_date'] = dict_coupon_info['download_start_date'].strftime('%Y-%m-%d %H:%M')
            dict_coupon_info['download_end_date'] = dict_coupon_info['download_end_date'].strftime('%Y-%m-%d %H:%M')
            dict_coupon_info['is_limited'] = '제한' if dict_coupon_info['is_limited'] == 0 else '무제한'
            dict_coupon_info['discount_price'] = f"{dict_coupon_info['discount_price']}원"

            res_coupon_list.append(dict_coupon_info)

        return res_coupon_list

    def get_coupon_detail(self, coupon_id, session):
        """
        쿠폰상세정보 조회 비즈니스 로직
            쿠폰상세정보 조회 DAO 메소드에서 전달받은 결과값을 controller에게 전달합니다.

        args :
            coupon_id : 상세정보를 조회할 쿠폰의 아이디
            session   : connection 형성된 session 객체

        returns :
            쿠폰상세정보

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-06 (이용민) : 초기 생성
        """

        coupon_detail = self.coupon_dao.select_coupon_detail(
            coupon_id, session)
        return coupon_detail

    def insert_coupon(self, coupon_info, session):
        """
        쿠폰등록 비즈니스 로직
            전달받은 쿠폰등록 정보를 가지고 쿠폰데이터를 생성하는 DAO메서드를 호출하는 비즈니스 로직입니다.

        args :
            coupon_info : 생성할 쿠폰 정보
            session     : connection 형성된 session 객체

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-07 (이용민) : 초기 생성
        """
        self.coupon_dao.insert_coupon(coupon_info, session)

    def update_coupon(self, coupon_info, session):
        """
        쿠폰정보수정 비즈니스 로직
            전달받은 쿠폰수정 정보를 가지고 쿠폰데이터를 수정하는 DAO메서드를 호출하는 비즈니스 로직입니다.

        args :
            coupon_info : 수정할 쿠폰 정보
            session     : connection 형성된 session 객체

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-07 (이용민) : 초기 생성
        """
        self.coupon_dao.update_coupon(coupon_info, session)
