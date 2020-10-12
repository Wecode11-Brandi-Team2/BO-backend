class CouponDao:

    def select_coupon_count(self, select_condition, session):

        query = """ SELECT 
                        count(id)
                    FROM 
                        coupons
                    WHERE
                        is_deleted = 0

                """

        condition_statement = ''

        if select_condition.get('couponId', None):
            condition_statement += f" AND coupons.id = {int(select_condition['couponId'])}"
            
        if select_condition.get('couponName', None):
            condition_statement += f" AND coupons.coupon_name LIKE '%{select_condition['couponName']}%'"

        if select_condition.get('validationStartFrom', None):
            condition_statement += f" AND coupons.validation_start_date >= '{select_condition['validationStartFrom']}' "

        if select_condition.get('validationStartTo', None):
            condition_statement += f" AND coupons.validation_start_date <= '{select_condition['validationStartTo']}' "

        if select_condition.get('validationEndFrom', None):
            condition_statement += f" AND coupons.validation_end_date >= '{select_condition['validationEndFrom']}' "

        if select_condition.get('validationEndTo', None):
            condition_statement += f" AND coupons.validation_end_date <= '{select_condition['validationEndTo']}' "

        if select_condition.get('downloadStartFrom', None):
            condition_statement += f" AND coupons.download_start_date >= '{select_condition['downloadStartFrom']}' "

        if select_condition.get('downloadStartTo', None):
            condition_statement += f" AND coupons.download_start_date <= '{select_condition['downloadStartTo']}' "

        if select_condition.get('downloadEndFrom', None):
            condition_statement += f" AND coupons.download_end_date >= '{select_condition['downloadEndFrom']}' "

        if select_condition.get('downloadEndTo', None):
            condition_statement += f" AND coupons.download_end_date <= '{select_condition['downloadEndTo']}' "

        if select_condition.get('IssueTypeId', None):
            condition_statement += f" AND coupons.issue_type_id = {select_condition['IssueTypeId']}"

        if select_condition.get('IsLimited', None):
            condition_statement += f" AND coupons.is_limited = {select_condition['IsLimited']}"

        query += condition_statement

        result = session.execute(query).fetchone()
        return result[0]

    def select_coupons(self, select_condition, session):
        """
        쿠폰리스트 조회 
            데이터베이스에서 쿠폰정보들을 조회합니다.

        args :
            session : connection 형성된 session 객체

        returns :
            쿠폰정보리스트

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-06 (이용민) : 초기 생성
        """

        query = """ SELECT
                        coupons.id AS coupon_id,
                        coupons.coupon_name,
                        coupons.discount_price,
                        coupons.validation_start_date,
                        coupons.validation_end_date, 
                        coupons.download_start_date,
                        coupons.download_end_date,
                        cit.issue_type_name,
                        coupons.is_limited, 
                        coupons.maximum_number,
                        coupons.issue_number,
                        coupons.used_number

                    FROM coupons

                    INNER JOIN coupon_issue_types AS cit
                    ON coupons.issue_type_id = cit.id

                    INNER JOIN coupon_issue_method AS cim
                    on coupons.issue_method_id = cim.id

                    WHERE
                        coupons.is_deleted = 0
                """


        condition_statement = ''

        if select_condition.get('couponId', None):
            condition_statement += f" AND coupons.id = {int(select_condition['couponId'])}"
            
        if select_condition.get('couponName', None):
            condition_statement += f" AND coupons.coupon_name LIKE '%{select_condition['couponName']}%'"

        if select_condition.get('validationStartFrom', None):
            condition_statement += f" AND coupons.validation_start_date >= '{select_condition['validationStartFrom']}' "

        if select_condition.get('validationStartTo', None):
            condition_statement += f" AND coupons.validation_start_date <= '{select_condition['validationStartTo']}' "

        if select_condition.get('validationEndFrom', None):
            condition_statement += f" AND coupons.validation_end_date >= '{select_condition['validationEndFrom']}' "

        if select_condition.get('validationEndTo', None):
            condition_statement += f" AND coupons.validation_end_date <= '{select_condition['validationEndTo']}' "

        if select_condition.get('downloadStartFrom', None):
            condition_statement += f" AND coupons.download_start_date >= '{select_condition['downloadStartFrom']}' "

        if select_condition.get('downloadStartTo', None):
            condition_statement += f" AND coupons.download_start_date <= '{select_condition['downloadStartTo']}' "

        if select_condition.get('downloadEndFrom', None):
            condition_statement += f" AND coupons.download_end_date >= '{select_condition['downloadEndFrom']}' "

        if select_condition.get('downloadEndTo', None):
            condition_statement += f" AND coupons.download_end_date <= '{select_condition['downloadEndTo']}' "

        if select_condition.get('IssueTypeId', None):
            condition_statement += f" AND coupons.issue_type_id = {select_condition['IssueTypeId']}"

        if select_condition.get('IsLimited', None):
            condition_statement += f" AND coupons.is_limited = {select_condition['IsLimited']}"


        condition_statement += ' ORDER BY coupons.id DESC '

        condition_statement += f" LIMIT 10 OFFSET {(select_condition['page']-1) * 10} "

        query += condition_statement
        
        # query 실행
        rows = session.execute(query).fetchall()

        return rows

    def select_coupon_detail(self, coupon_id, session):
        """
        쿠폰상세정보 조회 
            데이터베이스에서 쿠폰상세정보를 조회합니다.

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

        query = """ SELECT
                        coupons.id,
                        coupons.coupon_name,
                        coupons.validation_start_date,
                        coupons.validation_end_date, 
                        coupons.download_start_date,
                        coupons.download_end_date,
                        coupons.is_limited, 
                        coupons.maximum_number,
                        coupons.discount_price,
                        coupons.issue_type_id,
                        coupons.issue_method_id,
                        coupons.description,
                        coupons.min_cost

                    FROM coupons

                    WHERE coupons.id = :coupon_id
                """

        # query 실행
        row = session.execute(query, {
            'coupon_id': coupon_id
        }).fetchone()

        return row

    def insert_coupon(self, coupon_info, session):
        """
        쿠폰등록 DAO 
            전달받은 쿠폰등록 정보를 가지고 데이터베이스에 쿠폰데이터를 생성하는 DAO메서드입니다.

        args :
            coupon_info : 생성할 쿠폰 정보
            session     : connection 형성된 session 객체

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-07 (이용민) : 초기 생성
        """

        query = """ INSERT INTO 
                        brandi.coupons (
                            id,
                            coupon_name,
                            validation_start_date,
                            validation_end_date,
                            download_start_date,
                            download_end_date,
                            is_limited,
                            used_number.
                            maximum_number,
                            issue_number,
                            issue_type_id,
                            issue_method_id,
                            description,
                            discount_price,
                            min_cost,
                            created_at,
                            is_deleted
                        )

                    VALUES (
                        DEFAULT,
                        :coupon_name,
                        :validation_start_date,
                        :validation_end_date,
                        :download_start_date,
                        :download_end_date,
                        :is_limited,
                        0,
                        :maximum_number,
                        0,
                        :issue_type_id,
                        :issue_method_id,
                        :description,
                        :discount_price,
                        :min_cost,
                        now(),
                        0
                    )
                """

        session.execute(query, coupon_info)

    def update_coupon(self, coupon_info, session):
        """
        쿠폰수정 DAO 
            전달받은 쿠폰수정 정보를 가지고 데이터베이스에서 해당 쿠폰의 정보를 수정합니다.

        args :
            coupon_info : 생성할 쿠폰 정보
            session     : connection 형성된 session 객체

        Authors:
            eymin1259@gmail.com 이용민

        History:
            2020-10-07 (이용민) : 초기 생성
        """

        query = """ UPDATE 
                        coupons
                    SET
                        coupon_name = :coupon_name,
                        description = :description
                    WHERE
                        coupons.id = :coupon_id
                """

        session.execute(query, coupon_info)
