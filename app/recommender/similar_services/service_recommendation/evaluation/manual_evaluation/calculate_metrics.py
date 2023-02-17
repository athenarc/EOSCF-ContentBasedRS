import glob

import numpy as np
import pandas as pd


def dcg(recommendation):
    """
    Returns the Discounted cumulative gain DCG = Σ(relevance_pos/ln(pos+1)) for pos=1,...,N
    Args:
        recommendation:  numpy array of recommended services' relevance (not relevant:0, relevant:1) per position
    """
    # # Replace 1 with 2 (In cumulative gain formula 0 => Not relevant 1 => Near relevant 2 => Relevant)
    # recommendation[recommendation == 1] = 2

    def pos_score(relevance, pos):
        return relevance / np.log2(pos + 1) if pos != 0 else 0

    return np.array([pos_score(relevance, i+1) for i, relevance in enumerate(recommendation)]).sum()


def ndcg(recommendation):
    # Calculate the iDCG TODO change?
    idcg = dcg(np.array([1, 1, 1, 1, 1, 1]))

    return dcg(recommendation) / float(idcg)


def evaluate_one(recommendation):

    # Remove Nan values
    recommendation = recommendation[~np.isnan(recommendation)]

    return {
        "precision": sum(recommendation)/len(recommendation),
        "ndcg": ndcg(recommendation)
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
    # "precision_per_position": {f"precision_{pos}": pos_sum / float(rows_count_per_pos[pos]) for pos, (pos_name, pos_sum)
    #                            in enumerate(annotation_df.sum(skipna=True).items())},

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

    # Evaluation results of phase 1
    metadata_annotation_files_path = "app/recommender/similar_services/service_recommendation/evaluation/" \
                                     "manual_evaluation/storage/manual_evaluation_final_files/phase1_metadata/"
    metadata_annotation_files = glob.glob(metadata_annotation_files_path + '*')

    metadata_results = get_evaluations_results(metadata_annotation_files)

    # Evaluation results of phase 2
    text_annotation_files_path = "app/recommender/similar_services/service_recommendation/evaluation/" \
                                 "manual_evaluation/storage/manual_evaluation_final_files/phase2_text/"
    text_annotation_files = glob.glob(text_annotation_files_path + '*')

    text_results = get_evaluations_results(text_annotation_files)

    print("End")
