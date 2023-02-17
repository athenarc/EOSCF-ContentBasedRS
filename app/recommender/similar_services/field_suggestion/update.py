from app.recommender.similar_services.preprocessor.embeddings import \
    text_embeddings
from app.recommender.update.update import Update


class FieldSuggestionUpdate(Update):
    def initialize(self):
        text_embeddings.initialize_text_embeddings()

    def update(self):
        text_embeddings.create_text_embeddings()

    def update_for_new_service(self, service_id: int):
        text_embeddings.update_text_embedding(new_service_id=service_id)

    def revert(self):
        text_embeddings.delete_text_embeddings()
