from app.recommenders.algorithms.similar_services_retrieval.preprocessor.embeddings import \
    text_embeddings
from app.recommenders.update.update import Update


class ProjectAssistantUpdate(Update):
    def initialize(self):
        text_embeddings.initialize_text_embeddings()

    def update(self):
        text_embeddings.create_text_embeddings()

    def update_for_new_service(self, service_id: int):
        text_embeddings.update_text_embedding_for_one_service(new_service_id=service_id)

    def revert(self):
        text_embeddings.delete_text_embeddings()
