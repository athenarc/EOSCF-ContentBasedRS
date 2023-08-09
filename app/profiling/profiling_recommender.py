from app.recommenders.similar_services.recommendation_set_generation import create_recommendation_set
from app.databases.registry.registry_selector import get_registry
from app.routes.update import update as structures_update
import random
import time
import numpy as np
import pandas as pd


def profile_reranker(num_services=10, num_trials=4):
    """Profile re-ranking in recommender

    Args:
        num_services (int): Number of services to be tested
        num_trials (int): Number of trials to (or not) perform reranking for each service

    Returns:
        avg_recommendation_time (dict): Average execution time with/without re-ranking per service
    """
    db = get_registry()
    structures_update()

    total_services = db.get_catalog_id_mappings()
    selected_services = random.sample(list(total_services['id']), k=num_services)
    reranking_trials = [True] * num_trials + [False] * num_trials
    avg_recommendation_time = {}

    for service in selected_services:
        with_rerank = []
        without_rerank = []
        for rerank_trial in reranking_trials:
            tic = time.time()
            create_recommendation_set(viewed_service_id=service, do_rerank=rerank_trial)
            toc = time.time()
            if rerank_trial is True:
                with_rerank.append(toc - tic)
            else:
                without_rerank.append(toc - tic)
        avg_recommendation_time[service] = {
            'with_reranking': np.mean(with_rerank),
            'without_reranking': np.mean(without_rerank)
        }
    avg_recommendation_time = pd.DataFrame.from_dict(avg_recommendation_time)
    return avg_recommendation_time
