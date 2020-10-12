import jwt, re
from flask import request, g, jsonify
from config import SECRET, get_s3_resource

def login_required(Session):
    def inner_function(func):
        def wrapper(*args, **kwargs):
            access_token = request.headers.get('Authorization', None)
            session = Session()
            
            if access_token:
                try:
                    payload = jwt.decode(access_token, SECRET['SECRET_KEY'], algorithm = SECRET['ALGORITHMS'])
                    seller_no = payload['seller_info']

                    if session:
                        get_seller_info_stmt = ("""
                            SELECT 
                                s.id,
                                s.is_admin,
                                s.is_deleted,
                                si.manager_id
                            FROM 
                                sellers as s
                            INNER JOIN seller_info as si ON si.seller_id = s.id
                            WHERE s.id = :seller_no
                        """)
                        seller = dict(session.execute(get_seller_info_stmt, {'seller_no' : seller_no}).fetchone())
                        if seller:
                            if seller['is_deleted'] == 0:
                                g.seller_info = {
                                    'seller_no': seller_no,
                                    'is_admin': seller['is_admin'],
                                    'manager_id' : seller['manager_id']
                                }
                                session.close()
                                return func(*args, **kwargs)
                            return jsonify({'message': 'DELETED_ACCOUNT'}), 400
                        return jsonify({'message': 'ACCOUNT_DOES_NOT_EXIST'}), 404

                except jwt.InvalidTokenError:
                    return jsonify({'message': 'INVALID_TOKEN'}), 401

                return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 400
            return jsonify({'message': 'INVALID_TOKEN'}), 401
        return wrapper
    return inner_function

# 이미지 파일 업로드 가능한 확장자
ALLOWED_EXTENSIONS = ('jpg', 'jpeg')

def allowed_file(filename):
    if '.' in filename and filename.rsplit('.', 1)[1] not in ALLOWED_EXTENSIONS:
        return jsonify({'message': 'INVALID_EXTENSION'}), 400

# 에러 발생 시 S3 서버에 업로드된 이미지를 삭제하는 메소드
def delete_image_in_s3(images, new_images):
    s3_resource = get_s3_resource()

    if new_images:
        for new_image in new_images:
            if new_image not in images:
                # 이미지 url 에서 파일 이름을 가져온다.
                file_name = re.findall('https:\/\/brandi-images\.s3\.ap-northeast-2\.amazonaws\.com\/(.*)', new_image)
                s3_resource.delete_object(Bucket='brandi-images', Key=f'{file_name[0]}')
    else:
        for image in images:
            # 이미지 url 에서 파일 이름을 가져온다.
            file_name = re.findall('https:\/\/brandi-images\.s3\.ap-northeast-2\.amazonaws\.com\/(.*)', image)
            s3_resource.delete_object(Bucket='brandi-images', Key=f'{file_name[0]}')