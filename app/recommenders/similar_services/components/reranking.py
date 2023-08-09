import pandas as pd
from app.settings import APP_SETTINGS
from app.recommenders.algorithms.similar_services_retrieval.services_similarity import \
    services_similarity


def re_ranking(candidates, recommendations_num):
    """Re-rank recommendations w.r.t similarity and diversity of a service

    Args:
        candidates (series): service ids related to target (viewed) service and their similarity
        recommendations_num (int): number of recommendations to generate

    Returns:
        recommended_services (dict): recommended services ids and their quality score
    """
    diversity_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["DIVERSITY_WEIGHT"]
    viewed_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["VIEWED_WEIGHT"]
    metadata_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["METADATA_WEIGHT"]

    # R'
    recommended_services = {}

    b = 3
    pool_size = b * recommendations_num

    # C'
    top_k_similar_services = pd.Series(index=candidates.index[:pool_size])
    services_intrasimilarities = get_services_intrasimilarties(top_k_similar_services=top_k_similar_services,
                                                               viewed_weight=viewed_weight,
                                                               metadata_weight=metadata_weight)

    # Bounded Greedy Selection Algorithm
    for k in range(recommendations_num):
        for service_id in top_k_similar_services.index:
            # Calculate quality for each service in C'
            quality = quality_metric(candidates=candidates, current_service=service_id,
                                     relative_services=recommended_services,
                                     services_intrasimilarities=services_intrasimilarities,
                                     diversity_weight=diversity_weight)
            top_k_similar_services.loc[service_id] = quality
        # Get first service in C' w.r.t Quality metric
        first = top_k_similar_services.idxmax()

        # R = R + First(C') - Add service in recommendations R
        recommended_services[first] = top_k_similar_services.loc[first]

        # C' = C' - First(C') - Remove service from top k similar services C'
        top_k_similar_services.drop(first, inplace=True)

    recommended_services = pd.Series(recommended_services)
    # Re-order recommendations based on similarity to target service
    recommended_services = candidates.loc[recommended_services.index].sort_values(ascending=False)

    return recommended_services


def get_services_intrasimilarties(top_k_similar_services, viewed_weight, metadata_weight):
    services_intrasimilarities = pd.DataFrame(columns=top_k_similar_services.index)
    # K x K matrix
    for service in top_k_similar_services.index:
        compared_services = [s for s in top_k_similar_services.index if s != service]
        similarities = services_similarity(service, compared_services=compared_services, view_weight=viewed_weight,
                                           metadata_weight=metadata_weight)
        services_intrasimilarities.loc[service] = similarities
    services_intrasimilarities = services_intrasimilarities.fillna(1)
    return services_intrasimilarities


def quality_metric(candidates, current_service, relative_services, services_intrasimilarities, diversity_weight):
    """Quality metric that combines diversity and similarity

    quality = (1 - diversity_weight) * similarity(target_service, current_service) +
              diversity_weight * relative_diversity(current_service, relative_services)

    References:
        Bradley and Smyth. "Improving Recommendation Diversity", 2001

    Args:
        candidates (series): service ids related to target (viewed) service and their similarity
        current_service (int): current service id
        relative_services (dict): relative services ids
        services_intrasimilarities (dataframe): similarities inbetween relative services
        diversity_weight: float [0,1], the weight of the diversity vs. the similarity
    Returns:
        quality (float): quality metric
    """
    m = len(relative_services)

    # calculate relative diversity
    if m == 0:
        relative_diversity = 1
    else:
        diversities = []
        for rel_service in relative_services.keys():
            similarity = services_intrasimilarities.loc[[current_service, rel_service], [rel_service, current_service]]
            diversities.append(diversity_metric(similarity))

        relative_diversity = sum(diversities) / m

    target_current_similarity = candidates.loc[current_service]

    quality = (1 - diversity_weight) * target_current_similarity + diversity_weight * relative_diversity

    return quality


def diversity_metric(similarity_matrix):
    """Diversity metric of a set of services as defined by Bradley and Smyth.

    diversity = (sum_i^n sum_j^n dissimilarity(service_i, service_j))/ n/2 (n-1)

    References:
        Bradley and Smyth. "Improving Recommendation Diversity", 2001

    Args:
        similarity_matrix (dataframe): similarity matrix between pairs of services

    Returns:
        diversity (float): total diversity of a similarity matrix
    """
    n = len(similarity_matrix)
    dissimilarity_matrix = 1 - similarity_matrix

    if n == 1:
        diversity = dissimilarity_matrix.iloc[0][0]
    else:
        diversity = dissimilarity_matrix.to_numpy().sum() / ((n / 2) * (n - 1))
    return diversity
