from app.recommenders.algorithms.similar_services_retrieval.preprocessor.embeddings import (
    metadata_embeddings, text_embeddings)
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.reports import \
    monitoring_reports
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.similarities import (
    metadata_similarities, text_similarities)
from app.recommenders.update.update import Update


class ServicesRecommendationUpdate(Update):
    def initialize(self):
        metadata_embeddings.initialize_metadata_embeddings()
        metadata_similarities.MetadataSimilaritiesManager().initialize_similarities()

        text_embeddings.initialize_text_embeddings()
        text_similarities.TextSimilaritiesManager().initialize_similarities()

        monitoring_reports.initialise_ar_report()
        monitoring_reports.initialise_status_report()

    def update(self):
        metadata_embeddings.create_metadata_embeddings()
        metadata_similarities.MetadataSimilaritiesManager().create_similarities()

        text_embeddings.create_text_embeddings()
        text_similarities.TextSimilaritiesManager().create_similarities()

        monitoring_reports.update_status_report()
        monitoring_reports.update_ar_report()

    def update_for_new_service(self, service_id: int):
        metadata_embeddings.update_metadata_embedding_for_one_service(new_service_id=service_id)
        metadata_similarities.MetadataSimilaritiesManager().update_similarities_for_one_service(
            new_service_id=service_id)

        text_embeddings.update_text_embedding_for_one_service(new_service_id=service_id)
        text_similarities.TextSimilaritiesManager().update_similarities_for_one_service(
            new_service_id=service_id)

    def revert(self):
        metadata_embeddings.delete_metadata_embeddings()
        metadata_similarities.MetadataSimilaritiesManager().delete_similarities()

        text_embeddings.delete_text_embeddings()
        text_similarities.TextSimilaritiesManager().delete_similarities()

        monitoring_reports.delete_status_report()
        monitoring_reports.delete_ar_report()
