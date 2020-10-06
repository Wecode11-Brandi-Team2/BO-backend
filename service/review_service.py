class ReviewService:
    def __init__(self, review_dao):
        self.review_dao = review_dao

    def get_review_list(self, valid_param, session):
        review_list_result = self.review_dao.get_review_list(valid_param, session)
        return review_list_result