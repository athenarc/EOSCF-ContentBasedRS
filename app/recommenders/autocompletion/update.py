from app.recommenders.algorithms.similar_services_retrieval.preprocessor.embeddings import \
    text_embeddings
from app.recommenders.autocompletion.tag_suggestions.preprocessor import tag_structures
from app.recommenders.update.update import Update


class FieldSuggestionUpdate(Update):
    def initialize(self):
        text_embeddings.initialize_text_embeddings()
        tag_structures.TagStructuresManager().initialize_tag_structures()

    def update(self):
        text_embeddings.create_text_embeddings()
        tag_structures.TagStructuresManager().create_tags_structures()

    def update_for_new_service(self, service_id: int):
        text_embeddings.update_text_embedding_for_one_service(new_service_id=service_id)

    def revert(self):
        text_embeddings.delete_text_embeddings()
        tag_structures.TagStructuresManager().delete_tag_structures()
