import glob

import pandas as pd
import csv


def _get_relatability(annotation, relatability_columns):

    similar_services_ids = []
    dissimilar_services_ids = []
    for relatability_column in relatability_columns:
        if annotation[relatability_column] == 1:
            similar_services_ids.append(annotation[f"Id{relatability_column[len('Relatability'):]}"])
        elif annotation[relatability_column] == 0:
            dissimilar_services_ids.append(annotation[f"Id{relatability_column[len('Relatability'):]}"])
    return similar_services_ids, dissimilar_services_ids

def update_ground_truth(ground_truth, annotation_file):
    """
    Updates the structure with the known similar services of each service
    Args:
        ground_truth: dict, key: service_id, value: list, list of similar services' ids
        annotation_file: str, the name of the file with a manual annotation
    """

    # Read the annotation file
    annotation_df = pd.read_excel(annotation_file, sheet_name="Sheet1", engine='openpyxl')

    relatability_columns = [col for col in annotation_df if col.startswith("Relatability")]

    # Update the ground truth info
    for _, row in annotation_df.iterrows():
        viewed_service_id = row["Viewed Service Id"]
        similar_services_ids, dissimilar_services_ids = _get_relatability(row, relatability_columns)
        #  Update the similar services of the service with id <viewed_service_id>
        if viewed_service_id in ground_truth:
            ground_truth[viewed_service_id]["similar_services"] = list(set(similar_services_ids + ground_truth[viewed_service_id]["similar_services"]))
            ground_truth[viewed_service_id]["dissimilar_services"] = list(set(dissimilar_services_ids + ground_truth[viewed_service_id]["dissimilar_services"]))
        else:
            ground_truth[viewed_service_id] = {"similar_services": similar_services_ids,
                                               "dissimilar_services": dissimilar_services_ids}

    return ground_truth

if __name__ == '__main__':

    annotation_files = glob.glob("api/recommender/similar_services/service_recommendation/evaluation/manual_evaluation/storage/manual_evaluation_results/**/*.xlsx")

    ground_truth = {}
    for annotation_file in annotation_files:
        ground_truth = update_ground_truth(ground_truth, annotation_file=annotation_file)

    # Save ground truth to file
    ground_truth_df = pd.DataFrame(columns=["similar_services", "dissimilar_services"], index=list(ground_truth.keys()),
                                   data=list(ground_truth.values()))

    ground_truth_df.to_excel("api/recommender/similar_services/service_recommendation/evaluation/manual_evaluation/storage/ground_truth.xlsx",
                             index_label="service_id")