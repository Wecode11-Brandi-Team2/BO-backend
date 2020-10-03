class ProductService:
    def __init__(self, product_dao):
        self.product_dao = product_dao

    def insert_product(self, product_info, session):
        """ 상품 정보 insert

        Authors:
            고지원

        History:
            2020-10-03 (고지원): 초기 생성
        """
        self.product_dao.insert_product(product_info, session)

    def get_products(self, filter_dict, session):
        """ 상품 리스트 전달

        Authors:
            고지원

        History:
            2020-09-21 (고지원): 초기 생성
            2020-10-01 (고지원): JSON 응답 형식 정의
        """
        products = self.product_dao.get_products(filter_dict, session)

        return products

    def get_product(self, product_id, session):
        """ 상품 데이터 전달

        Authors:
            고지원

        History:
            2020-09-23 (고지원): 초기 생성
        """
        product = self.product_dao.get_product(product_id, session)
        return product

    def make_excel(self, id_list, session):
        """ 상품 정보 엑셀 파일 다운로드

        특정 아이디의 상품 정보를 엑셀 파일로 다운로드합니다.

        Authors:
            고지원

        History:
            2020-10-03 (고지원): 초기 생성
        """

        # excel 파일을 만들기 위한 패키지
        import pandas as pd

        # make excel file
        writer = pd.ExcelWriter('../excels_products.xlsx')

        # 선택 상품 필터링을 위한 딕셔너리
        filter_dict = {
            'product_id': id_list
        }

        df = pd.DataFrame({
            "등록일": product.created_at,
            "대표이미지": product.main_img,
            "상품명": product.name,
            "상품코드": product.product_code,
            "상품번호": product.id,
            "셀러속성": product.attribution_name,
            "셀러명": product.korean_name,
            "판매가": product.price,
            "할인가": product.discount_price,
            "판매여부": product.is_on_sale,
            "진열여부": product.is_displayed,
            "할인여부": product.is_promotion} for product in self.product_dao.get_products(filter_dict, session))

        df.to_excel(writer, 'sheet1')
        writer.save()