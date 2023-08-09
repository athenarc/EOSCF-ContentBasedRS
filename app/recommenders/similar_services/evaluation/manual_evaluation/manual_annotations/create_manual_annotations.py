import glob
import random
from collections import defaultdict

import pandas as pd
from app.databases.registry.registry_selector import get_registry
from app.recommenders.similar_services.recommendation_set_generation import \
    create_recommendation_set
from app.routes.update import update as structures_update
from app.settings import APP_SETTINGS, update_backend_settings
from tqdm import tqdm

CONFIG_DIR = \
    'app/recommenders/similar_services/evaluation/manual_evaluation/manual_annotations/configs/'
GOLD_SERVICES_PATH = \
    'app/recommenders/similar_services/evaluation/manual_evaluation/storage/gold_services.csv'
OUTPUT_DIR = \
    'app/recommenders/similar_services/evaluation/manual_evaluation/manual_annotations/storage/'
GROUND_TRUTH_PATH = \
    'app/recommenders/similar_services/evaluation/manual_evaluation/storage/ground_truth.xlsx'
ANNOTATORS_POOL = ['Anna', 'Katerina', 'Mike']
ANNOTATOR_OVERLAP = 2


def get_recommendations(viewed_service_id):
    # Get the produced recommendations for the viewed service
    recommendations = create_recommendation_set(viewed_service_id, recommendations_num=6)

    # Get the names of the viewed a recommended services
    db = get_registry()
    services_with_names = db.get_services_by_ids(ids=[viewed_service_id] +
                                                     [rec_item["service_id"] for rec_item in recommendations],
                                                 attributes=["service_id", "name"])

    return {
        'viewed_service_id': viewed_service_id,
        'viewed_service_name': services_with_names[services_with_names["service_id"] == viewed_service_id].iloc[0][
            "name"],
        'recommendations': [
            [rec_item["service_id"],
             services_with_names[services_with_names["service_id"] == rec_item["service_id"]].iloc[0]["name"]]
            for rec_item in recommendations
        ]
    }


def generate_column_names(recommendations_numb=6):
    columns = ['Viewed Service Id', 'Viewed Service Name']
    for _ in range(recommendations_numb):
        columns += ['Id', 'Name', 'Relatability']

    return columns


def get_ground_truth_relatability(viewed_service, recommended_service, relatability_ground_truth_df):
    try:
        similar_services = relatability_ground_truth_df[relatability_ground_truth_df["service_id"]
                                                        == viewed_service]["similar_services"].values[0]
        dissimilar_services = relatability_ground_truth_df[relatability_ground_truth_df["service_id"]
                                                           == viewed_service]["dissimilar_services"].values[0]
        relatability = None
        if recommended_service in similar_services:
            relatability = 1
        elif recommended_service in dissimilar_services:
            relatability = 0
        return relatability
    except KeyError:
        return None


def flatten_recommendations_to_row(recommendation_result, relatability_ground_truth_df):
    row = [recommendation_result['viewed_service_id'], recommendation_result['viewed_service_name']]
    for rec in recommendation_result['recommendations']:
        relatability = get_ground_truth_relatability(viewed_service=recommendation_result['viewed_service_id'],
                                                     recommended_service=rec[0],
                                                     relatability_ground_truth_df=relatability_ground_truth_df)
        row += rec + [relatability]

    return row


def get_annotators():
    return random.sample(ANNOTATORS_POOL, k=ANNOTATOR_OVERLAP)


def create_evaluation_dfs(service_ids, relatability_ground_truth_df):
    recommendations_per_annotator = defaultdict(list)
    for service_id in service_ids:
        recs = get_recommendations(service_id)
        evaluation_row = flatten_recommendations_to_row(recs, relatability_ground_truth_df)

        annotators = get_annotators()
        for annotator in annotators:
            recommendations_per_annotator[annotator].append(evaluation_row)

    eval_dfs = {annotator: pd.DataFrame(eval_data, columns=generate_column_names(recommendations_numb=6))
                for annotator, eval_data in recommendations_per_annotator.items()}

    return eval_dfs


def create_version_df():
    version_info = {
        'METADATA_USED': ",".join(APP_SETTINGS['BACKEND']['SIMILAR_SERVICES']['METADATA']),
        'TEXT_ATTRIBUTES_USED': ",".join(APP_SETTINGS['BACKEND']['SIMILAR_SERVICES']['TEXT_ATTRIBUTES']),
        'METADATA_WEIGHT': APP_SETTINGS['BACKEND']['SIMILAR_SERVICES']['METADATA_WEIGHT'],
        'MODEL': APP_SETTINGS['BACKEND']['SIMILAR_SERVICES']['SBERT']['MODEL_NAME'],
        'NOTES': APP_SETTINGS['BACKEND'].get("NOTES", "")  # NOTES might not be filled in config
    }
    return pd.DataFrame.from_dict(version_info, orient='index')


def write_excel(sheets, out_file):
    writer = pd.ExcelWriter(out_file, engine='xlsxwriter')
    for sheet_name, df in sheets.items():
        write_index = sheet_name == 'version'
        df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0, index=write_index)
    writer.save()


def generate_excel(config_file, gold_service_ids, out_file):
    # We need to update all our structures for the new config
    update_backend_settings(config_file)
    structures_update()

    # Read ground_truth relatabilities
    relatability_ground_truth_df = pd.read_excel(GROUND_TRUTH_PATH, sheet_name="Sheet1", engine='openpyxl')

    version_df = create_version_df()
    evaluations_dfs = create_evaluation_dfs(gold_service_ids, relatability_ground_truth_df)

    write_excel({'version': version_df} | evaluations_dfs, out_file)


def iterate_over_configs(config_dir):
    gold_service_ids = pd.read_csv(GOLD_SERVICES_PATH)['id']

    config_files = glob.glob(config_dir + '*')
    print("Config files given:")
    print(config_files)

    for path in tqdm(config_files):
        generate_excel(path, gold_service_ids, OUTPUT_DIR + path.split('/')[-1][:-5] + '.xlsx')


if __name__ == '__main__':
    # --config_file parameter needs to be filled
    # You can point it to any valid config file (it will not be taken into account for creating the evaluation files)
    iterate_over_configs(CONFIG_DIR)
