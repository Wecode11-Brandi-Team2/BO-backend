class ReviewService:
    def __init__(self, review_dao):
        self.review_dao = review_dao

    def get_review_list(self, valid_param, session):
        """
        Review list 반환해주는 함수

        controller에서 받은 인자를 dao로 받고, dao에서의 return 값을 controller로 전달해주는 함수

        Args:
            valid_param : validate_params에서 통과 한 QueryString.
            session : db connection 객체
        Returns:
            get_review_result : 글 번호, 셀러명, 상품명, 회원닉네임, 리뷰내용, 등록일시, 수정일시 return (r'type : dict)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-07 (hj885353@gmail.com) : 초기 생성
        """
        review_list_result = self.review_dao.get_review_list(valid_param, session)
        return review_list_result

    def review_info(self, review_no, session):
        """
        리뷰 내용 보기 버튼 눌렀을 때, 모달창에 띄워지는 데이터를 반환해주는 함수

        controller에서 받은 인자를 dao로 받고, dao에서의 return 값을 controller로 전달해주는 함수

        Args:
            review_no : validate_params에서 통과 한 path_parameter.
            session : db connection 객체
        Returns:
            review_info_result : 글 번호, 리뷰 내용 return (r'type : dict)
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-08 (hj885353@gmail.com) : 초기 생성
        """
        review_info_result = self.review_dao.review_info(review_no, session)
        return review_info_result

    def delete_review(self, review_no, session):
        """
        리뷰 내용 삭제 API

        리뷰 삭제 버튼을 눌렀을 때, 해당 글 번호를 path_parameter로 받아 해당 글을 soft delete 처리한다.
        controller에서 받은 parameter를 dao로 전달한다.

        Args:
            review_no : validate_params에서 통과 한 path_parameter.
            session : db connection 객체
        Returns:
            
        Authors:
            hj885353@gmail.com (김해준)
        History:
            2020-10-08 (hj885353@gmail.com) : 초기 생성
        """
        delete_review_result = self.review_dao.delete_review(review_no, session)