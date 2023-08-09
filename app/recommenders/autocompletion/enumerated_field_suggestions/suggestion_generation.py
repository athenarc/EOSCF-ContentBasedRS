from app.databases.registry.registry_selector import get_registry
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.embeddings.text_embeddings import \
    create_text_embedding
from app.recommenders.autocompletion.enumerated_field_suggestions.similar_services import \
    get_similar_services
from app.recommenders.autocompletion.enumerated_field_suggestions.suggestion_candidates import \
    get_candidates
from app.settings import APP_SETTINGS


def get_suggestions_for_enumerated_fields(new_service, requested_fields, maximum_suggestions=5,
                                          existing_fields_values=None,
                                          evaluation_mode=False, similarity_threshold=None,
                                          considered_services_threshold=None, frequency_threshold=None):
    """
    Args:
        new_service: dict with the name and value for each filled field of a service
        requested_fields: list<str>, the names of the fields for which auto-completion will be implemented
        maximum_suggestions: int, the maximum number of suggestions per field
        existing_fields_values: dict with the name and the current values of each field
        evaluation_mode: boolean
        similarity_threshold: float, the similarity threshold to be considered for all the fields
        considered_services_threshold: int, the number of services to be considered for the selection
                                       of the fields values
        frequency_threshold: float, the required frequency threshold of the values in the considered services
                             for all fields

    Returns: dict with the names and suggested values for all requested fields
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
    similar_services = db.get_services_by_ids(ids=all_similar_services_ids,
                                              attributes=requested_fields,
                                              remove_generic_attributes=True)

    # Find the most used values for every requested field
    suggestions = {}
    for requested_field in requested_fields:
        if existing_fields_values is not None and requested_field in existing_fields_values:
            existing_values = existing_fields_values[requested_field]
        else:
            existing_values = None

        field_suggestions = get_candidates(
            field_values=similar_services[similar_services["service_id"]
            .isin(similar_services_ids_per_field[requested_field])][requested_field]
            .values.tolist(),
            frequency_threshold=APP_SETTINGS["BACKEND"]["AUTO_COMPLETION"]["ENUMERATED_FIELDS"]
            [requested_field]["FREQUENCY_THRESHOLD"],
            existing_values=existing_values)

        suggestions[requested_field] = field_suggestions \
            if len(field_suggestions) <= maximum_suggestions else field_suggestions[:maximum_suggestions]

    return suggestions
