import pandas as pd
from api.databases.redis_db import get_object


def re_ranking(target_service, candidates, recommendations_num):
    """Re-rank recommendations w.r.t similarity and diversity of a service

    Args:
        target_service (id): target service id
        candidates (dict): service ids related to target service and their similarity
        recommendations_num (int): number of recommendations to generate

    Returns:
        recommended_services (dict): recommended services ids and their quality score
    """
    _metadata_similarities = get_object('METADATA_SIMILARITY')
    _text_similarities = get_object('TEXT_SIMILARITY')

    # R'
    recommended_services = {}

    b = 3
    pool_size = b * recommendations_num

    # C'
    top_k_similar_services = pd.Series(index=candidates.index[:pool_size])

    # Bounded Greedy Selection Algorithm
    for k in range(recommendations_num):
        for service_id in top_k_similar_services.index:
            # Calculate quality for each service in C'
            quality = quality_metric(
                target_service=target_service,
                current_service=service_id,
                relative_services=recommended_services,
                metadata_similarities=_metadata_similarities,
                text_similarities=_text_similarities
            )
            top_k_similar_services.loc[service_id] = quality
        # Get first service in C' w.r.t Quality metric
        first = top_k_similar_services.idxmax()

        # R = R + First(C') - Add service in recommendations R
        recommended_services[first] = top_k_similar_services.loc[first]

        # C' = C' - First(C') - Remove service from top k similar services C'
        top_k_similar_services.drop(first, inplace=True)

    recommended_services = pd.Series(recommended_services)

    return recommended_services


def quality_metric(target_service, current_service, relative_services, metadata_similarities, text_similarities):
    """Quality metric that combines diversity and similarity

    quality = 1/2 * similarity(target_service, current_service) +
              1/2 * relative_diversity(current_service, relative_services)

    References:
        Bradley and Smyth. "Improving Recommendation Diversity", 2001

    Args:
        target_service (int): target service id
        current_service (int): current service id
        relative_services (dict): relative services ids
        metadata_similarities (dataframe): metadata services
        text_similarities (dataframe):
    Returns:
        quality (float): quality metric
    """
    m = len(relative_services)

    # calculate relative diversity
    if m == 0:
        relative_diversity = 1
    else:
        diversities = []
        for rel_service in relative_services:
            sim = 1 / 2 * metadata_similarities.loc[current_service][rel_service] + \
                  1 / 2 * text_similarities.loc[current_service][rel_service]
            sim_df = pd.DataFrame([sim])
            diversities.append(diversity_metric(sim_df))
        relative_diversity = sum(diversities) / m

    # calculate similarity of target service and current service
    target_current_similarity = 1 / 2 * metadata_similarities.loc[target_service][current_service] + \
                                1 / 2 * text_similarities.loc[target_service][current_service]

    quality = 1 / 2 * target_current_similarity + 1 / 2 * relative_diversity

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
