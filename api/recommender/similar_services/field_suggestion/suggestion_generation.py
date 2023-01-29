from api.databases.registry.registry_selector import get_registry
from api.recommender.similar_services.field_suggestion.similar_services import get_similar_services
from api.recommender.similar_services.preprocessor.embeddings.text_embeddings import \
    create_text_embedding
from api.recommender.similar_services.field_suggestion.suggestion_candidates import \
    get_candidates
from api.settings import APP_SETTINGS


def get_auto_complete_suggestions(new_service, requested_fields, maximum_suggestions=5, evaluation_mode=False,
                                  similarity_threshold=None,
                                  considered_services_threshold=None, frequency_threshold=None):
    """
    @param new_service: dict with the name and value for each filled field of a service
    @param requested_fields: list<str>, the names of the fields for which auto-completion will be done
    @param maximum_suggestions: int, the maximum number of suggestions per field
    @return: dict with the names and suggested values for all requested fields
    """

    # Calculate the text embedding of the new service
    text_embedding = create_text_embedding(new_service)

    # Get similar services ids
    similar_services_ids_per_field = get_similar_services(requested_fields, text_embedding, similarity_threshold,
                                                          considered_services_threshold)

    if evaluation_mode:
        # Remove evaluated service from similar services of every field
        for _, similar_services in similar_services_ids_per_field.items():
            if new_service["service_id"] in similar_services:
                similar_services.remove(new_service["service_id"])

    # Get the requested fields for all similar services
    all_similar_services_ids = list(
        set().union(*[similar_services for _, similar_services in similar_services_ids_per_field.items()]))

    db = get_registry()
    similar_services = db.get_services_by_ids(ids=all_similar_services_ids, attributes=requested_fields)

    # Find the most used values for every requested field
    suggestions = {}
    for requested_field in requested_fields:
        field_suggestions = get_candidates(similar_services[similar_services["service_id"]
                                           .isin(similar_services_ids_per_field[requested_field])][requested_field]
                                           .values.tolist(), APP_SETTINGS["BACKEND"]["AUTO_COMPLETION"]
                                           [requested_field]["FREQUENCY_THRESHOLD"])

        suggestions[requested_field] = field_suggestions \
            if len(field_suggestions) <= maximum_suggestions else field_suggestions[:maximum_suggestions]

    return suggestions
