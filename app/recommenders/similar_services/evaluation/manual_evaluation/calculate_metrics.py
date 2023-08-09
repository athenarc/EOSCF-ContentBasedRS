import glob

import numpy as np
import pandas as pd

EVALUATION_RESULTS_DIR = "app/recommenders/similar_services/evaluation/manual_evaluation/storage/metrics"

EXPERIMENTS_DIRS = [
    "app/recommenders/similar_services/evaluation/manual_evaluation/storage/manual_evaluation_final_files"
    "/phase1_metadata",
    "app/recommenders/similar_services/evaluation/manual_evaluation/storage/manual_evaluation_final_files"
    "/phase2_text",
    "app/recommenders/similar_services/evaluation/manual_evaluation/storage/manual_evaluation_final_files"
    "/phase3_metadata_weight",
    "app/recommenders/similar_services/evaluation/manual_evaluation/storage/manual_evaluation_final_files"
    "/phase4_diversity_weight",
    "app/recommenders/similar_services/evaluation/manual_evaluation/storage/manual_evaluation_final_files"
    "/phase5_tf-idf",
]


def dcg(recommendation_set):
    """
    Returns the Discounted cumulative gain DCG = Σ(relevance_pos/ln(pos+1)) for pos=1,...,N
    Args:
        recommendation_set:  numpy array of recommended services' relevance (not relevant:0, relevant:1) per position
    """
    # # Replace 1 with 2 (In cumulative gain formula 0 => Not relevant 1 => Near relevant 2 => Relevant)
    # recommendation_set[recommendation == 1] = 2

    def pos_score(relevance, pos):
        return relevance / np.log2(pos + 1) if pos != 0 else 0

    return np.array([pos_score(relevance, i+1) for i, relevance in enumerate(recommendation_set)]).sum()


def ndcg(recommendation_set):
    # Calculate the iDCG TODO change?
    idcg = dcg(np.array([1, 1, 1, 1, 1, 1]))

    return dcg(recommendation_set) / float(idcg)


def evaluate_one(recommendation_set):

    # Remove Nan values
    recommendation_set = recommendation_set[~np.isnan(recommendation_set)]

    return {
        "precision": sum(recommendation_set)/len(recommendation_set),
        "ndcg": ndcg(recommendation_set)
    }


def evaluation(annotation_file):
    """
    Returns the evaluation results
    Args:
        annotation_file: str, the name of the file with the annotations
    """

    # Read the annotation file
    annotation_df = pd.read_excel(annotation_file, sheet_name="Sheet1", engine='openpyxl')

    # Get the relatability columns
    relatability_columns = [col for col in annotation_df if col.startswith("Relatability")]
    annotation_df = annotation_df[relatability_columns]

    evaluation_results = {"precision": [], "ndcg": []}
    for _, result in annotation_df.iterrows():
        metrics = evaluate_one(result.to_numpy())
        evaluation_results["precision"].append(metrics["precision"])
        evaluation_results["ndcg"].append(metrics["ndcg"])

    # Count values in each column
    rows_count_per_pos = annotation_df.count()
    # "precision_per_position": {f"precision_{pos}": pos_sum / float(rows_count_per_pos[pos]) for pos, (pos_name,
    # pos_sum) in enumerate(annotation_df.sum(skipna=True).items())},

    results = {
        "avg_precision": sum(evaluation_results["precision"]) / float(len(evaluation_results["precision"])),
        "avg_ndcg": sum(evaluation_results["ndcg"]) / float(len(evaluation_results["ndcg"]))
    }

    results.update({f"precision_{pos}": pos_sum / float(rows_count_per_pos[pos])
                    for pos, (pos_name, pos_sum) in enumerate(annotation_df.sum(skipna=True).items())})

    return results


def get_evaluations_results(annotation_files):
    results = {}
    for annotation_file in annotation_files:
        results[annotation_file.split("/")[-1][:-5]] = evaluation(annotation_file)

    # Create table for comparison
    comp_table = pd.DataFrame.from_records(index=list(results.keys()), data=list(results.values()))

    return comp_table


if __name__ == '__main__':

    for experiment_dir in EXPERIMENTS_DIRS:
        annotation_files = glob.glob(experiment_dir + '/*')
        results = get_evaluations_results(annotation_files)
        # Save evaluation results
        results.to_excel(f"{EVALUATION_RESULTS_DIR}/{experiment_dir.split('/')[-1]}_evaluation_results.xlsx",
                         index_label="Version")
