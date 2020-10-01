class ProductService:
    def __init__(self, product_dao):
        self.product_dao = product_dao

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