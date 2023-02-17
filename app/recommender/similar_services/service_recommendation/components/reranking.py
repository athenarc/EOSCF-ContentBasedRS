import pandas as pd
from app.recommender.similar_services.service_recommendation.components.resources_similarity import \
    resources_similarity
from app.settings import APP_SETTINGS


def re_ranking(target_service, purchases, candidates, recommendations_num, viewed_weight, metadata_weight):
    """Re-rank recommendations w.r.t similarity and diversity of a service

    Args:
        target_service (id): target service id
        purchases (list): list of ids of purchased services
        candidates (dict): service ids related to target service and their similarity
        recommendations_num (int): number of recommendations to generate
        viewed_weight: float [0,1], the weight of the viewed resource similarity in the score calculation
        metadata_weight: float [0,1], the weight of the metadata similarity in the score calculation
    Returns:
        recommended_services (dict): recommended services ids and their quality score
    """
    diversity_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["DIVERSITY_WEIGHT"]

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
                purchases=purchases,
                relative_services=recommended_services,
                metadata_weight=metadata_weight,
                viewed_weight=viewed_weight,
                diversity_weight=diversity_weight
            )
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


def quality_metric(target_service, current_service, purchases, relative_services,
                   viewed_weight, metadata_weight, diversity_weight):
    """Quality metric that combines diversity and similarity

    quality = (1 - diversity_weight) * similarity(target_service, current_service) +
              diversity_weight * relative_diversity(current_service, relative_services)

    References:
        Bradley and Smyth. "Improving Recommendation Diversity", 2001

    Args:
        target_service (int): target service id
        current_service (int): current service id
        purchases (list): list of ids of purchased services
        relative_services (dict): relative services ids
        viewed_weight: float [0,1], the weight of the viewed resource similarity in the score calculation
        metadata_weight: float [0,1], the weight of the metadata similarity in the score calculation
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
        similarity = resources_similarity(resource=current_service,
                                          compared_resources=list(relative_services.keys()),
                                          view_weight=viewed_weight,
                                          metadata_weight=metadata_weight).values

        similarity_df = pd.DataFrame([similarity])
        diversities.append(diversity_metric(similarity_df))
        relative_diversity = sum(diversities) / m

    # calculate similarity of target service and current service
    target_current_similarity = resources_similarity(resource=target_service,
                                                     purchased_resources=purchases,
                                                     compared_resources=[current_service],
                                                     view_weight=viewed_weight,
                                                     metadata_weight=metadata_weight).values

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
