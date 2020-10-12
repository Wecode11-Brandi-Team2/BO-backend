import re

from werkzeug.utils import secure_filename
from flask import request

from config import get_s3_resource
from utils import allowed_file

class ProductService:
    def __init__(self, product_dao):
        self.product_dao = product_dao

    def get_first_categories(self, seller_info, session):
        """ 상품 등록 시 셀러의 속성에 맞는 첫 번째 카테고리 리스트 전달

        Authors:
            고지원

        History:
            2020-10-04 (고지원): 초기 생성
        """
        first_categories = self.product_dao.get_first_categories(seller_info, session)

        return first_categories

    def get_second_categories(self, seller_info, session):
        """ 상품 등록 시 첫 번째 카테고리에 해당하는 두 번째 카테고리 리스트 전달

        Authors:
            고지원

        History:
            2020-10-04 (고지원): 초기 생성
        """
        second_categories = self.product_dao.get_second_categories(seller_info, session)

        return second_categories

    def get_sellers(self, q, session):
        """ 셀러 데이터 전달

        Authors:
            고지원

        History:
            2020-10-04 (고지원): 초기 생성
        """
        sellers = self.product_dao.get_sellers(q, session)

        return sellers

    def insert_product(self, product_info, session):
        """ 상품 정보 insert

        Authors:
            고지원

        History:
            2020-10-03 (고지원): 초기 생성
        """
        self.product_dao.insert_product(product_info, session)

    def update_product(self, product_info, session):
        """ 상품 정보 수정

        상품 수정 시 새로운 이미지와 기존 이미지 리스트를 비교하여 s3에서 이미지를 삭제하고 새로운 상품 이력을 등록합니다.

        Authors:
            고지원

        History:
            2020-10-10 (고지원): 초기 생성
        """
        s3_resource = get_s3_resource()

        # 기존 이미지가 새로운 이미지 리스트에 없을 경우 s3에서 삭제한다.
        for old_img in product_info['images']:

            # 이미지 url 에서 파일 이름을 가져온다.
            file_name = re.findall('https:\/\/brandi-images\.s3\.ap-northeast-2\.amazonaws\.com\/(.*)', old_img)

            if old_img not in product_info['new_images']:

                # 기존 이미지가 새로운 이미지 리스트에 없을 경우 s3 서버에서 이미지를 삭제한다.
                s3_resource.delete_object(Bucket = 'brandi-images', Key = f'{file_name[0]}')

        self.product_dao.update_product(product_info, session)

    def upload_image(self, product_code, images):
        """ s3에 이미지를 업로드

        S3 서버에 이미지를 업로드 하고 데이터베이스에 저장될 이미지 url 리스트를 반환한다.

        Authors:
            고지원

        History:
            2020-10-05 (고지원): 초기 생성
            2020-10-09 (고지원): 이미지 url 상품 코드와 파일의 이름 조합으로 수정
        """
        image_urls = list()

        # s3 서버 연결 및 이미지 업로드
        s3_resource = get_s3_resource()

        for image in images:
            # 허용된 jpg, jpeg 확장자인지 확인한다.
            message = allowed_file(image.filename)

            # jpg, jpeg 확장자가 아닐 경우 에러 메세지가 반환된다.
            if message:
                return message

            # 해킹으로부터 파일 이름 보호
            image_filename = secure_filename(image.filename)

            # s3 서버에 이미지 업로드
            s3_resource.put_object(Body = image, Bucket = 'brandi-images', Key = f'{product_code}_{image_filename}', ContentType = 'image/jpeg')

            # 데이터베이스에 저장할 이미지 url 을 리스트에 추가한다.
            image_url = f'https://brandi-images.s3.ap-northeast-2.amazonaws.com/{product_code}_{image_filename}'
            image_urls.append(image_url)

        return image_urls

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
        """ 상품 상세 데이터 전달

        Authors:
            고지원

        History:
            2020-10-03 (고지원): 초기 생성
        """
        product = self.product_dao.get_product(product_id, session)

        return product

    def get_product_history(self, product_id, session):
        """ 상품 수정 이력 전달

        Authors:
            고지원

        History:
            2020-10-10 (고지원): 초기 생성
        """

        history = self.product_dao.get_product_history(product_id, session)

        return history

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