from app.recommender.similar_services.preprocessor.embeddings import (
    metadata_embeddings, text_embeddings)
from app.recommender.similar_services.preprocessor.reports import \
    monitoring_reports
from app.recommender.similar_services.preprocessor.similarities import (
    metadata_similarities, text_similarities)
from app.recommender.update.update import Update


class ServicesRecommendationUpdate(Update):
    def initialize(self):
        metadata_embeddings.initialize_metadata_embeddings()
        metadata_similarities.initialize_metadata_similarities()
        text_embeddings.initialize_text_embeddings()
        text_similarities.initialize_text_similarities()
        monitoring_reports.initialise_ar_report()
        monitoring_reports.initialise_status_report()

    def update(self):
        metadata_embeddings.create_metadata_embeddings()
        metadata_similarities.create_metadata_similarities()
        text_embeddings.create_text_embeddings()
        text_similarities.create_text_similarities()
        monitoring_reports.update_status_report()
        monitoring_reports.update_ar_report()

    def update_for_new_service(self, service_id: int):
        metadata_embeddings.update_metadata_embedding(new_service_id=service_id)
        metadata_similarities.update_metadata_similarities(new_service_id=service_id)
        text_embeddings.update_text_embedding(new_service_id=service_id)
        text_similarities.update_text_similarities(new_service_id=service_id)

    def revert(self):
        metadata_embeddings.delete_metadata_embeddings()
        metadata_similarities.delete_metadata_similarities()
        text_embeddings.delete_text_embeddings()
        text_similarities.delete_text_similarities()
        monitoring_reports.delete_status_report()
        monitoring_reports.delete_ar_report()
