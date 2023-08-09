import glob
import os

import pandas as pd
from app.recommenders.similar_services.recommendation_set_generation import \
    create_recommendation_set
from app.routes.update import update as structures_update
from app.settings import update_backend_settings
from tqdm import tqdm

GOLD_SERVICES_PATH = \
    'app/recommenders/similar_services/evaluation/manual_evaluation/storage/' \
    'gold_services.csv'
CONFIG_DIR = \
    'app/recommenders/similar_services/evaluation/manual_evaluation/storage/' \
    'manual_evaluation_configs/'
XLS_DIR = \
    'app/recommenders/similar_services/evaluation/manual_evaluation/storage/' \
    'manual_evaluation_final_files/'


def get_recommendations(viewed_service_id):
    # Get the produced recommendations for the viewed service
    recommendations = create_recommendation_set(viewed_service_id, recommendations_num=6)

    return [rec["service_id"] for rec in recommendations]


def iterate_over_configs(config_dir, xls_dir):
    gold_service_ids = pd.read_csv(GOLD_SERVICES_PATH)['id']

    config_files = glob.glob(config_dir + '/*')
    print("Config files given:")
    print(config_files)

    for config_file in tqdm(config_files):
        # We need to update all our structures for the new config
        update_backend_settings(config_file)
        structures_update()

        service_ids = pd.read_csv(GOLD_SERVICES_PATH)['id']

        # Get the recommendations for all services
        recs = {}
        for service_id in service_ids:
            recs[service_id] = get_recommendations(service_id)

        # read the excel related to this config
        evaluation = pd.read_excel(f'{xls_dir}/{config_file.split("/")[-1][:-5]}.xlsx', sheet_name="Sheet1")
        evaluation = evaluation.rename(columns={"Id": "Id.0", "Name": "Name.0",
                                                "Relatability": "Relatability.0"})

        # for each row of the dataframe
        for index, row in evaluation.iterrows():
            # Change the position of the recommendations
            service_recommendations = recs[row["Viewed Service Id"]]
            updated_row = row.copy()
            # For every saved recommendation
            for pos in [0, 1, 2, 3, 4, 5]:
                # Get the actual position
                true_pos = service_recommendations.index(row[f"Id.{pos}"])
                # Place it in the right position
                updated_row[f"Id.{true_pos}"] = row[f"Id.{pos}"]
                updated_row[f"Name.{true_pos}"] = row[f"Name.{pos}"]
                updated_row[f"Relatability.{true_pos}"] = row[f"Relatability.{pos}"]

            evaluation.loc[index] = updated_row.values

        evaluation = evaluation.rename(columns={"Id.0": "Id", "Name.0": "Name",
                                                "Relatability.0": "Relatability"})
        # Save the xls file
        evaluation.to_excel(f'{xls_dir}/{config_file.split("/")[-1][:-5]}_corrected.xlsx')


if __name__ == '__main__':

    phases = [d for d in os.listdir(CONFIG_DIR) if os.path.isdir(os.path.join(CONFIG_DIR, d))]

    for phase_configs in phases:
        iterate_over_configs(CONFIG_DIR+phase_configs, XLS_DIR+phase_configs)
