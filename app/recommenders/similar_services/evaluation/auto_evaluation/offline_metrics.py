import glob

import numpy as np
import pandas as pd
from app.databases.registry.registry_selector import get_registry
from app.recommenders.algorithms.similar_services_retrieval.services_similarity import \
    services_similarity
from app.recommenders.similar_services.recommendation_set_generation import \
    create_recommendation_set
from app.routes.update import update as structures_update
from app.settings import APP_SETTINGS, update_backend_settings
from tqdm import tqdm
from tqdm.auto import tqdm

CONFIG_DIR = "app/recommender/similar_services/service_recommendation/evaluation/auto_evaluation/storage/configs/"


def diversity(services_ids):
    metadata_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["METADATA_WEIGHT"]
    viewed_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["VIEWED_WEIGHT"]
    recommendations_diversities = []
    print('Calculating diversity..')
    for service_id in tqdm(services_ids.values):
        rec_services = create_recommendation_set(service_id[0])
        rec_services_ids = [service['service_id'] for service in rec_services]
        diversities = []
        for rec_service_id in rec_services_ids:
            compared_services = [service for service in rec_services_ids if service != rec_service_id]

            similarity = services_similarity(service=rec_service_id,
                                             compared_services=compared_services,
                                             view_weight=viewed_weight,
                                             metadata_weight=metadata_weight)
            diversities.append(1 - similarity.mean())
        recommendations_diversities.append(np.mean(diversities))

    return np.mean(recommendations_diversities)


def coverage(services_ids):
    recommended_services = set()
    print('Calculating coverage..')
    for service_id in tqdm(services_ids.values):
        rec_services_list = create_recommendation_set(service_id[0])
        for rec_service_elm in rec_services_list:
            recommended_services.add(rec_service_elm['service_id'])
    coverage_percentage = len(recommended_services) / len(services_ids)

    return coverage_percentage


def main():
    config_files = glob.glob(CONFIG_DIR + '*')
    results_df = pd.DataFrame(columns=['config', 'coverage', 'diversity'])
    results_df['config'] = config_files

    # We first generate the recommendations for all the configs given
    for config_file in tqdm(results_df['config']):
        print(f'Evaluating recommender with config: {config_file}')
        update_backend_settings(config_file)
        structures_update()
        reg = get_registry()
        services_ids = reg.get_services()
        results_df.loc[results_df['config'] == config_file, 'coverage'] = coverage(services_ids)
        results_df.loc[results_df['config'] == config_file, 'diversity'] = diversity(services_ids)
        results_df.to_csv(
            'app/recommender/similar_services/service_recommendation/evaluation/auto_evaluation/storage/results/'
            'results.csv')
