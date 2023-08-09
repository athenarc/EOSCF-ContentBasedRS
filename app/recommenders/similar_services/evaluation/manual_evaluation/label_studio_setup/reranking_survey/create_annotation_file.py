import glob
import json
import random
from collections import defaultdict

import pandas as pd
from app.recommenders.similar_services.evaluation.manual_evaluation.label_studio_setup.reranking_survey.reranking_survey_model import \
    RerankingSurveyModel

RECOMMENDATIONS_PER_DIVERSITY_DIR = \
    'app/recommenders/similar_services/evaluation/manual_evaluation/label_studio_setup/storage/reranking_results'
OUTPUT_SURVEY_FILES_DIR = \
    'app/recommenders/similar_services/evaluation/manual_evaluation/label_studio_setup/storage/survey_files/'
ANNOTATORS = ["Mike", "Katerina", "Anna"]
ANNOTATOR_OVERLAP = 2


def extract_diversity(file_path):
    return int(file_path.split('/')[-1].split('.')[0])


def prepare_xlsx_file_to_dict(file_path):
    df = pd.read_excel(file_path, sheet_name="User")
    df = df[[col for col in df.columns if "Id" in col]]

    return df


def get_viewed_services_ids(df):
    """
    Assumption: All recommendation files in RESULTS_FILE_DIR must have the exact same viewed services.
    """
    return list(df['Viewed Service Id'])


def get_list_of_recommended_ids(viewed_service_id, df):
    row = df.loc[df['Viewed Service Id'] == viewed_service_id]
    return list(row[[col for col in row.columns if 'Id.' in col or "Id" == col]].iloc[0])


def generate_annotations():
    file_paths = glob.glob(f"{RECOMMENDATIONS_PER_DIVERSITY_DIR}/*.xlsx")

    df_per_diversity_dict = {}
    for file_path in file_paths:
        df_per_diversity_dict[extract_diversity(file_path)] = prepare_xlsx_file_to_dict(file_path)

    service_ids = get_viewed_services_ids(list(df_per_diversity_dict.values())[0])

    final_annotations = []
    for service_id in service_ids:
        recommendations_per_diversity = {}
        for diversity, df in df_per_diversity_dict.items():
            recommendations_per_diversity[diversity] = get_list_of_recommended_ids(service_id, df)

        survey_model = RerankingSurveyModel(viewed_service_id=service_id,
                                            services_per_diversity=recommendations_per_diversity,
                                            total_candidates=len(file_paths))

        final_annotations.append({
            "data": survey_model.to_dict(deduplication=True)
        })

    return final_annotations


def store_annotations_per_annotator(annotations):
    annotations_per_annotator = defaultdict(list)

    for annotation in annotations:
        annotators = random.sample(ANNOTATORS, ANNOTATOR_OVERLAP)
        for annotator in annotators:
            annotations_per_annotator[annotator].append(annotation)

    for annotator, annotations in annotations_per_annotator.items():
        with open(f"{OUTPUT_SURVEY_FILES_DIR}{annotator}.json", 'w') as f:
            json.dump(annotations, f)


def main():
    all_annotations = generate_annotations()
    store_annotations_per_annotator(all_annotations)


if __name__ == '__main__':
    main()
