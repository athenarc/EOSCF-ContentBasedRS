import glob
import json
from collections import defaultdict

EVALUATIONS_PER_ANNOTATOR = \
    'app/recommenders/similar_services/evaluation/manual_evaluation/label_studio_setup/storage/survey_results/'


def read_evaluation_files():
    file_paths = glob.glob(f"{EVALUATIONS_PER_ANNOTATOR}*.json")

    evaluations = []
    for file_path in file_paths:
        with open(file_path) as f:
            evaluations.extend(json.load(f))

    return evaluations


def get_chosen_diversities(choice, shuffled_diversities, duplicate_pairs):
    choice = int(choice[-1])
    diversity = shuffled_diversities[choice - 1]

    ret_diversities = {diversity}
    for pair in duplicate_pairs:
        if diversity == pair[0]:
            ret_diversities.add(pair[1])
        elif diversity == pair[1]:
            ret_diversities.add(pair[0])

    return ret_diversities


def extract_eval_info(evaluations):
    eval_info = []

    for evaluation in evaluations:
        eval_info.append({
            "service_name": evaluation["data"]["name"],
            "chosen_diversities": get_chosen_diversities(
                evaluation["annotations"][0]["result"][0]["value"]["choices"][0],
                evaluation["data"]["shuffled_diversities"],
                evaluation["data"]["duplicate_pairs"]
            )
        })

    return eval_info


def merge_evaluations(evaluations_per_annotator):
    evaluations = defaultdict(list)

    for evaluation in evaluations_per_annotator:
        evaluations[evaluation["service_name"]].append(evaluation["chosen_diversities"])

    conflicts = 0
    merged_evaluations = {}

    for service_name, diversities_picked in evaluations.items():
        if diversities_picked[0] != diversities_picked[1]:
            merged_evaluations[service_name] = diversities_picked[0].union(diversities_picked[1])
            conflicts += 1
        else:
            merged_evaluations[service_name] = diversities_picked[0]
            if 75 in diversities_picked[0]:
                print(service_name)

    diversity_scores = defaultdict(lambda: 0)
    for _, diversities_picked in merged_evaluations.items():
        for picked_diversity in diversities_picked:
            diversity_scores[picked_diversity] += 1

    print(f"Conflicts: {conflicts}")
    print(f"Diversity scores:\n {diversity_scores}")


def main():
    evaluations = read_evaluation_files()
    eval_info = extract_eval_info(evaluations)
    merge_evaluations(eval_info)


if __name__ == '__main__':
    main()
