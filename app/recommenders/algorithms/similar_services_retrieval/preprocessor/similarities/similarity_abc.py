from abc import ABC


class SimilaritiesManager(ABC):
    def create_similarities(self):
        pass

    def update_similarities_for_one_service(self, new_service_id):
        pass

    def initialize_similarities(self):
        pass

    @staticmethod
    def existence_similarities():
        pass

    def get_similarities(self):
        pass

    @staticmethod
    def store_similarities(similarities):
        pass

    @staticmethod
    def delete_similarities():
        pass
