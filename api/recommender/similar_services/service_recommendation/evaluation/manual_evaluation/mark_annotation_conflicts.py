import glob

import pandas as pd

ANNOTATORS_POOL = ["Anna", "Katerina", "Mike"]


def mark_annotation_conflicts(annotation_file):
    # Read annotation files
    annotation_lists = pd.read_excel(annotation_file, sheet_name=ANNOTATORS_POOL, engine='openpyxl')

    # Union annotation files
    annotation_df = pd.concat(annotation_lists)

    relatability_columns = [col for col in annotation_df if col.startswith("Relatability")]

    # Find conflicts
    annotations_by_service = annotation_df.groupby("Viewed Service Id")
    conflicts = []
    for service, service_annotations in annotations_by_service:
        # Check if the annotators agree
        count_annotation_values = service_annotations[relatability_columns].nunique()
        non_unique_annotation_values = count_annotation_values[count_annotation_values > 1]
        # If there are conflicts in the annotation of a recommendation
        if non_unique_annotation_values.shape[0]:
            for annotated_column_name in non_unique_annotation_values.index:
                conflicts.append((service, annotated_column_name))

    # Union annotations for same service
    annotation_df = annotation_df.drop_duplicates(subset="Viewed Service Id")

    # Empty and mark cells with conflicts
    for viewed_service_id, relatability_column in conflicts:
        annotation_df.loc[annotation_df["Viewed Service Id"] == viewed_service_id, relatability_column] = None
    annotation_df = annotation_df.reset_index(drop=True)

    # # Highlight cells with None values
    annotation_df = annotation_df.style.highlight_null()

    # Save file
    writer = pd.ExcelWriter(f"{annotation_file[:-5]}_marked_conflicts.xlsx", engine='xlsxwriter')
    annotation_df.to_excel(writer)

    writer.save()


if __name__ == '__main__':
    # --config_file parameter needs to be filled
    # You can point it to any valid config file (it will not be taken into account for creating the evaluation files)
    annotation_files_path = "api/recommender/similar_services/service_recommendation/evaluation/" \
                            "manual_evaluation/storage/manual_evaluation_results/"

    annotation_files = glob.glob(annotation_files_path + '*')
    for annotation_file in annotation_files:
        mark_annotation_conflicts(annotation_file=annotation_file)
