from flask import jsonify, Blueprint, request
from flask_request_validator import (
    GET,
    Param,
    Enum,
    Pattern,
    validate_params
)

from utils import login_required


def create_product_endpoints(product_service, Session):

    product_app = Blueprint('product_app', __name__, url_prefix='/api/product')

    @product_app.route('/products', methods = ['GET'])
    # @login_required(Session)
    @validate_params(
        Param('limit', GET, int, default=10, required=False),
        Param('offset', GET, int, required=False),
        Param('is_displayed', GET, int, rules=[Enum(0, 1)], required=False),
        Param('is_promotion', GET, int, rules=[Enum(0, 1)], required=False),
        Param('is_on_sale', GET, int, rules=[Enum(0, 1)], required=False),
        Param('seller_attribute', GET, int, rules=[Enum(0, 1)], required=False),
        Param('select', GET, int, rules=[Enum(0, 1, 2)], required=False),
        Param('q', GET, required=False),
        Param('seller_name', GET, required=False),
        Param('period_start', GET, str, rules=[Pattern(r"^\d\d\d\d-\d{1,2}-\d{1,2}$")], required=False),
        Param('period_end', GET, str, rules=[Pattern(r"^\d\d\d\d-\d{1,2}-\d{1,2}$")], required=False)
    )
    def products(*args):
        """ 상품 정보 전달 API

        쿼리 파라미터로 필터링에 사용될 값을 받아 필터링된 상품의 데이터 리스트를 표출합니다.

        args:
            *args:
                limit: pagination 을 위한 파라미터
                offset: pagination 을 위한 파라미터
                is_displayed: 진열 여부
                is_promotion: 할인 여부
                is_on_sale: 판매 여부
                seller_attribute: 셀러 속성 id
                select: 상품 검색 시 상품 명, 코드, 번호 중 어떤 것을 선택했는지 판단 위한 파라미터
                q: 상품 검색을 위한 파라미터
                seller_name: 셀러 이름 검색을 위한 파라미터

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
            filter_dict = {}

            # pagination
            filter_dict['limit'] = args[0]
            filter_dict['offset'] = args[1]

            # 진열 여부
            filter_dict['is_displayed'] = args[2]

            # 할인 여부
            filter_dict['is_promotion'] = args[3]

            # 판매 여부
            filter_dict['is_on_sale'] = args[4]

            # 셀러 속성
            filter_dict['seller_attribute'] = args[5]

            # 상품 검색
            filter_dict['select'] = args[6]

            # 상품 검색어
            filter_dict['q'] = args[7]

            # 셀러 검색어
            filter_dict['seller_name'] = args[8]

            # 조회 기간 시작
            filter_dict['period_start'] = args[9]

            # 조회 기간 끝
            filter_dict['period_end'] = args[10]

            body = [{
                'created_at'       : product.created_at,
                'main_image'       : product.main_img,
                'product_name'     : product.name,
                'product_code'     : product.product_code,
                'product_id'       : product.id,
                'attribution_name' : product.attribution_name,
                'seller_name'      : product.korean_name,
                'price'            : product.price,
                'discount_price'   : product.discount_price,
                'is_displayed'     : product.is_displayed,
                'is_on_sale'       : product.is_on_sale,
                'is_promotion'     : product.is_promotion
            } for product in product_service.get_products(filter_dict, session)]

            return jsonify(body), 200

        except Exception as e:
            return jsonify({'message' : f'{e}'}), 500

        finally:
            session.close()

    @product_app.route('/<int:product_id>', methods=['GET'])
    # @login_required(Session)
    def product(product_id):
        """ 상품 정보 전달 API

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
            product = product_service.get_product(product_id, session)

            body = {
                'id'              : product['p_id'],
                'product_code'    : product['p_code'],
                'is_on_sale'      : product['is_on_sale'],
                'product_name'    : product['name'],
                'simple_desc'     : product['simple_description'],
                'images'          : product['images'],
                'price'           : product['price'],
                'detail_desc'     : product['detail_description'],
                'discount_price'  : product['discount_price'],
                'discount_rate'   : product['discount_rate'],
                'is_definite'     : product['is_definite'],
                'min_unit'        : product['min_unit'],
                'max_unit'        : product['max_unit'],
                'first_category'  : product['first_category_name'],
                'second_category' : product['second_category_name']
            }

            return jsonify(body), 200

        except Exception as e:
            return jsonify({'message': f'{e}'}), 500

        finally:
            session.close()

    @product_app.route('/excel', methods=['GET'])
    # @login_required(Session)
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

            # make_excel 함수를 호출한다.
            product_service.make_excel(id_list, session)

            return jsonify({'message': 'SUCCESS'}), 200

        except Exception as e:
            return jsonify({'message': f'{e}'}), 500

        finally:
            session.close()

    @product_app.route('', methods=['POST', 'UPDATE'])
    # @login_required(Session)
    def insert_product():
        session = Session()
        try:
            if request.method == 'POST':

                # 상품 입력을 위한 데이터를 받는다.
                product_info = {
                    'seller_id'          : request.json['seller_id'],
                    'is_on_sale'         : request.json['is_on_sale'],
                    'is_displayed'       : request.json['is_displayed'],
                    'name'               : request.json['name'],
                    'simple_description' : request.json['simple_description'],
                    'detail_description' : request.json['detail_description'],
                    'price'              : request.json['price'],
                    'discount_rate'      : request.json['discount_rate'],
                    'discount_price'     : request.json['discount_price'],
                    'min_unit'           : request.json['min_unit'],
                    'max_unit'           : request.json['max_unit'],
                    'is_stock_managed'   : request.json['is_stock_managed'],
                    'stock_number'       : request.json['stock_number'],
                    'first_category_id'  : request.json['first_category_id'],
                    'second_category_id' : request.json['second_category_id'],
                    'modifier_id'        : request.json['modifier_id'],
                    'images'             : request.json['images']
                }

                product_service.insert_product(product_info, session)

        except KeyError:
            return jsonify({'message' : 'KEY_ERROR'}), 400

        # except Exception as e:
        #     session.rollback()

            # return jsonify({'message': f'{e}'}), 500

        finally:
            session.close()

    return product_app