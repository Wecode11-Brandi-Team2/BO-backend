import re
import uuid

from sqlalchemy import exc
from flask import jsonify, Blueprint, request
from flask_request_validator import (
    GET,
    Param,
    Enum,
    Pattern,
    validate_params
)

from utils import login_required, allowed_file

def create_product_endpoints(product_service, Session):

    product_app = Blueprint('product_app', __name__, url_prefix='/api/product')

    @product_app.route('/products', methods = ['GET'], endpoint='products')
    @login_required(Session)
    @validate_params(
        Param('filterLimit', GET, int, default=10, required=False),
        Param('page', GET, int, required=False),
        Param('exhibitionYn', GET, int, rules=[Enum(0, 1)], required=False),
        Param('exhibitionYn', GET, int, rules=[Enum(0, 1)], required=False),
        Param('sellYn', GET, int, rules=[Enum(0, 1)], required=False),
        Param('mdSeNo', GET, int, required=False),
        Param('selectFilter', GET, str, rules=[Enum('productName', 'productNo', 'productCode')], required=False),
        Param('filterKeyword', GET, required=False),
        Param('mdName', GET, required=False),
        Param('filterDateFrom', GET, str, rules=[Pattern(r"^\d\d\d\d-\d{1,2}-\d{1,2}$")], required=False),
        Param('filterDateTo', GET, str, rules=[Pattern(r"^\d\d\d\d-\d{1,2}-\d{1,2}$")], required=False)
    )
    def products(*args):
        """ 상품 정보 리스트 전달 API

        쿼리 파라미터로 필터링에 사용될 값을 받아 필터링된 상품의 데이터 리스트를 표출합니다.

        args:
            *args:
                filterLimit: pagination 을 위한 파라미터
                page: pagination 을 위한 파라미터
                exhibitionYn: 진열 여부
                discountYn: 할인 여부
                sellYn: 판매 여부
                mdSeNo: 셀러 속성 id
                selectFilter: 상품 검색 시 상품 명, 코드, 번호 중 어떤 것을 선택했는지 판단 위한 파라미터
                filterKeyword: 상품 검색을 위한 파라미터
                mdName: 셀러 이름 검색을 위한 파라미터
                filterDateFrom: 조회 기간 시작
                filterDateTo: 조회 기간 끝

        returns :
            200: 상품 리스트
            500: Exception

        Authors:
            고지원

        History:
            2020-10-01 (고지원): 초기 생성
        """
        try:
            session = Session()

            # 필터링을 위한 딕셔너리
            filter_dict = dict()

            # pagination
            filter_dict['filterLimit'] = args[0]
            filter_dict['page'] = args[1]

            # 진열 여부
            filter_dict['exhibitionYn'] = args[2]

            # 할인 여부
            filter_dict['discountYn'] = args[3]

            # 판매 여부
            filter_dict['sellYn'] = args[4]

            # 셀러 속성
            filter_dict['mdSeNo'] = args[5]

            # 상품 검색
            filter_dict['selectFilter'] = args[6]

            # 상품 검색어
            filter_dict['filterKeyword'] = args[7]

            # 셀러 검색어
            filter_dict['mdName'] = args[8]

            # 조회 기간 시작
            filter_dict['filterDateFrom'] = args[9]

            # 조회 기간 끝
            filter_dict['filterDateTo'] = args[10]

            body = [dict(product) for product in product_service.get_products(filter_dict, session)]

            return jsonify(body), 200

        except Exception as e:
            return jsonify({'message' : f'{e}'}), 500

        finally:
            session.close()

    @product_app.route('/<int:product_id>', methods=['GET'], endpoint='product')
    @login_required(Session)
    def product(product_id):
        """ 상품 수정 시 기존 등록 정보 전달 API

        path parameter 로 id 받아 해당 상품의 데이터 표출합니다.

        args:
            product_id : 상품의 id

        returns :
            200: 상품 정보
            500: Exception

        Authors:
            고지원

        History:
            2020-10-01 (고지원): 초기 생성
        """
        session = Session()
        try:
            # 상품 데이터
            body = dict(product_service.get_product(product_id, session))

            return jsonify(body), 200

        except Exception as e:
            return jsonify({'message': f'{e}'}), 500

        finally:
            session.close()

    @product_app.route('/excel', methods=['GET'], endpoint='make_excel')
    @login_required(Session)
    def make_excel():
        """ 상품 정보 엑셀 다운로드 API

        전체 상품 또는 선택 상품의 정보를 excel 파일로 다운로드 합니다.

        args:
            product_id : 상품의 id 리스트

        returns :
            200: Excel 파일 다운
            500: Exception

        Authors:
            고지원

        History:
            2020-10-02 (고지원): 초기 생성
        """
        session = Session()
        try:
            # 선택한 상품들의 id를 list 로 받는다.
            id_list = request.args.getlist('product_id')

            # service 의 make_excel 함수를 호출한다.
            product_service.make_excel(id_list, session)

            return jsonify({'message': 'SUCCESS'}), 200

        except Exception as e:
            return jsonify({'message': f'{e}'}), 500

        finally:
            session.close()

    @product_app.route('/seller', methods=['GET'], endpoint='sellers')
    @login_required(Session)
    @validate_params(
        Param('q', GET, str, required = True)
    )
    def sellers(*args):
        """ 셀러 리스트 전달 API
        query parameter 를 받아 필터링된 셀러 리스트 데이터를 표출합니다.

        args:
            *args:
                name: 셀러명 검색을 위한 쿼리 스트링

        returns :
            200: 셀러 리스트
            500: Exception

        Authors:
            고지원

        History:
            2020-10-04 (고지원): 초기 생성
        """
        session = Session()
        try:
            # 필터링을 위한 딕셔너리
            seller_dict = dict()
            seller_dict['name'] = args[0]

            # 셀러 데이터
            body = [dict(seller) for seller in product_service.get_sellers(seller_dict, session)]

            return jsonify(body), 200

        except Exception as e:
            return jsonify({'message': f'{e}'}), 500

        finally:
            session.close()

    @product_app.route('/category', methods=['GET'], endpoint='product_categories')
    @login_required(Session)
    def product_categories():
        """ 1차, 2차 카테고리 정보 전달 API

        셀러의 속성 아이디를 받아 1차 카테고리, 1차 카테고리 아이디를 받아 2차 카테고리 정보를 전달한다.

        args:
            seller_attr_id: 셀러의 속성 id
            f_category_id: 1차 카테고리 id

        returns :
            200: 1차 또는 2차 카테고리 정보
            500: Exception

        Authors:
            고지원

        History:
            2020-10-04 (고지원): 초기 생성
        """
        session = Session()
        try:
            # 셀러 속성 아이디 또는 1차 카테고리 아이디를 받는다.
            seller_attr_id = request.args.get('seller_attr_id')
            f_category_id = request.args.get('f_category_id')

            # 셀러 속성 아이디가 들어왔을 경우 1차 카테고리 정보를 반환
            if seller_attr_id:
                body = [{
                    'id'   : cat.f_id,
                    'name' : cat.first_category_name
                } for cat in product_service.get_first_categories(seller_attr_id, session)]

                return jsonify(body), 200

            # 1차 카테고리 아이디가 들어왔을 경우 2차 카테고리 정보를 반환
            body = [{
                'id'   : cat.s_id,
                'name' : cat.second_category_name
            } for cat in product_service.get_second_categories(f_category_id, session)]

            return jsonify(body), 200

        except Exception as e:
            return jsonify({'message': f'{e}'}), 500

        finally:
            session.close()

    @product_app.route('', methods=['POST'], endpoint='insert_product')
    @login_required(Session)
    def insert_product():
        """ 상품 정보 등록 API

        returns :
            200: 상품 정보를 데이터베이스에 저장
            400:
                NAME_CANNOT_CONTAIN_QUOTATION_MARK,
                START_DATE_CANNOT_BE_EARLIER_THAN_END_DATE,
                CANNOT_SET_MORE_THAN_20,
                CANNOT_SET_LESS_THAN_10,
                DISCOUNT_RANGE_CAN_BE_SET_FROM_0_TO_99,
                DUPLICATE_DATA
            500: Exception

        Authors:
            고지원

        History:
            2020-10-03 (고지원): 초기 생성
            2020-10-04 (고지원): 상품 정보 입력 시 제한 사항 에러 추가
        """
        session = Session()
        try:
            # 상품명에 ' 또는 " 포함 되었는지 체크
            pattern = re.compile('[\"\']')
            if pattern.search(request.form['name']):
                return jsonify({'message': 'NAME_CANNOT_CONTAIN_QUOTATION_MARK'}), 400

            # 할인 시작일이 할인 종료일보다 빠를 경우
            if request.form['discount_start_date'] > request.form['discount_end_date']:
                return jsonify({'message': 'START_DATE_CANNOT_BE_EARLIER_THAN_END_DATE'}), 400

            # 최소 수량 또는 최대 수량이 20을 초과할 경우
            if int(request.form['min_unit']) > 20 or int(request.form['max_unit']) > 20:
                return jsonify({'message': 'CANNOT_SET_MORE_THAN_20'}), 400

            # 판매가가 10원 미만일 경우
            if int(request.form['price']) < 10:
                return jsonify({'message': 'CANNOT_SET_LESS_THAN_10'}), 400

            # 할인률이 0 ~ 99% 가 아닐 경우
            if int(request.form['discount_rate']) not in range(0, 99):
                return jsonify({'message': 'DISCOUNT_RANGE_CAN_BE_SET_FROM_0_TO_99'}), 400

            # 상품 코드
            product_code = str(uuid.uuid4())

            # S3 이미지 저장
            image_urls = list()

            for idx in range(1, 6):
                image = request.files.get(f'image_{idx}', None)

                if image:
                    # 허용된 확장자인지 확인 (png, jpg, jpeg)
                    allowed_file(image.filename)
                    image_url = product_service.save_product_image(image, product_code)
                    image_urls.append(image_url)

            print(image_urls)

            # 상품 입력을 위한 데이터를 받는다.
            product_info = {
                'seller_id': request.form['seller_id'],
                'is_on_sale': request.form['is_on_sale'],
                'is_displayed': request.form['is_displayed'],
                'name': request.form['name'],
                'simple_description': request.form['simple_description'],
                'detail_description': request.form['detail_description'],
                'price': request.form['price'],
                'is_definite' :request.form['is_definite'],
                'discount_rate': request.form['discount_rate'],
                'discount_price': request.form['discount_price'],
                'min_unit': request.form['min_unit'],
                'max_unit': request.form['max_unit'],
                'is_stock_managed': request.form['is_stock_managed'],
                'stock_number': request.form['stock_number'],
                'first_category_id': request.form['first_category_id'],
                'second_category_id': request.form['second_category_id'],
                'modifier_id': request.form['modifier_id'],
                'images': image_urls,
                'discount_start_date': request.form['discount_start_date'],
                'discount_end_date': request.form['discount_end_date'],
                'product_code': product_code
            }

            product_service.insert_product(product_info, session)

            session.commit()

            return jsonify({'message': 'SUCCESS'}), 200

        except KeyError:
            return jsonify({'message': 'KEY_ERROR'}), 400

        except exc.IntegrityError:
            return jsonify({'message': 'DUPLICATE_DATA'}), 400

        except exc.InvalidRequestError:
            return jsonify(({'message': 'INVALID_REQUEST'})), 400

        except exc.ProgrammingError:
            return jsonify(({'message': 'ERROR_IN_SQL_SYNTAX'})), 500

        except Exception as e:
            session.rollback()

            return jsonify({'message': f'{e}'}), 500

        finally:
            session.close()

    return product_app