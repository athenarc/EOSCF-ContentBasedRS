import glob

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from app.recommender.similar_services.service_recommendation.recommendation_generation import \
    create_recommendation
from app.routes.update import update as structures_update
from app.settings import update_backend_settings
from tqdm import tqdm

GOLD_SERVICES_PATH = \
    'app/recommender/similar_services/service_recommendation/evaluation/manual_evaluation/storage/gold_services.csv'
CONFIG_DIR = \
    "app/recommender/similar_services/service_recommendation/evaluation/manual_evaluation/" \
    "recommender_version_distances/configs/"
RECOMMENDATIONS_STORE_DIR = \
    'app/recommender/similar_services/service_recommendation/evaluation/manual_evaluation/' \
    'recommender_version_distances/storage/produced_recommendations/'
RESULTS_DIR = \
    'app/recommender/similar_services/service_recommendation/evaluation/manual_evaluation/' \
    'recommender_version_distances/storage/results/'


def difference_of_sets(rec_list_1, rec_list_2):
    """
    From 0 to 1:
        * 0 -> all the recommendations were common
        * 1 -> no common recommendations
    """
    rec_set_1 = set(rec_list_1)
    rec_set_2 = set(rec_list_2)

    return 1 - len(rec_set_1.intersection(rec_set_2)) / len(rec_set_1.union(rec_set_2))


def damerau_levenshtein(rec_list_1, rec_list_2):
    """
        Source: https://web.archive.org/web/20150909134357/http://mwh.geek.nz:80/2009/04/26/python-damerau-levenshtein-distance/

        This distance is the number of additions, deletions, substitutions,
        and transpositions needed to transform the first sequence into the
        second.

        Transpositions are exchanges of *consecutive* characters; all other
        operations are self-explanatory.
    """
    one_ago = None
    this_row = list(range(1, len(rec_list_2) + 1)) + [0]
    for x in range(len(rec_list_1)):
        # Python lists wrap around for negative indices, so put the
        # leftmost column at the *end* of the list. This matches with
        # the zero-indexed strings and saves extra calculation.
        two_ago, one_ago, this_row = one_ago, this_row, [0] * len(rec_list_2) + [x + 1]
        for y in range(len(rec_list_2)):
            del_cost = one_ago[y] + 1
            add_cost = this_row[y - 1] + 1
            sub_cost = one_ago[y - 1] + (rec_list_1[x] != rec_list_2[y])
            this_row[y] = min(del_cost, add_cost, sub_cost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and rec_list_1[x] == rec_list_2[y - 1]
                    and rec_list_1[x - 1] == rec_list_2[y] and rec_list_1[x] != rec_list_2[y]):
                this_row[y] = min(this_row[y], two_ago[y - 2] + 1)

    return this_row[len(rec_list_2) - 1] / max(len(rec_list_2), len(rec_list_1))


def dissimilarity_of_two_sets(recommendation_lists_1, recommendation_lists_2, distance_metric):
    """
    Care: The recommendations between the two lists must be aligned
    """
    dissimilarities = [
        distance_metric(rec1, rec2) for rec1, rec2 in zip(recommendation_lists_1, recommendation_lists_2)
    ]

    return sum(dissimilarities) / len(dissimilarities)


def pairwise_dissimilarities(recommendation_lists, distance_metric):
    """
    Args:
        distance_metric: Difference of sets, Damerau-Levenshtein
        recommendation_lists: The list of all the recommendations from the different variations generated

    Returns:
        The pairwise dissimilarity matrix
    """

    dissimilarities_matrix = []
    for rec_list_1 in recommendation_lists:
        dissimilarities_matrix.append(
            [
                dissimilarity_of_two_sets(rec_list_1, rec_list_2, distance_metric)
                for rec_list_2 in recommendation_lists
            ]
        )

    return dissimilarities_matrix


def plot_pairwise_similarities(dissimilarities_matrix, variations_names=None):
    axes_labels = variations_names if variations_names is not None else False
    sns.heatmap(dissimilarities_matrix,
                xticklabels=axes_labels,
                yticklabels=axes_labels,
                vmin=0, vmax=1, annot=True)
    plt.show()


def get_recommendations(viewed_service_id):
    # Get the produced recommendations
    recommendation = create_recommendation(viewed_service_id, recommendations_num=6)
    # Return a list with the ids of the recommended services
    return [rec_item["service_id"] for rec_item in recommendation]


def store_recommendations(gold_service_ids, store_path):
    recommendations_of_gold_services = [get_recommendations(viewed_service_id)
                                        for viewed_service_id in gold_service_ids]

    pd.DataFrame(recommendations_of_gold_services).to_csv(store_path, header=False, index=False)


def find_dissimilar_variations(dir_path, distance_metric):
    rec_files = glob.glob(dir_path + '*')
    all_variations_recs = []
    variation_names = []
    for file_path in rec_files:
        recs_df = pd.read_csv(file_path, header=0, index_col=0)
        all_variations_recs.append(recs_df.values.tolist())

        variation_names.append(file_path.split('/')[-1].replace('.csv', ''))

    dissimilarities = pairwise_dissimilarities(
        recommendation_lists=all_variations_recs,
        distance_metric=distance_metric
    )

    plot_pairwise_similarities(dissimilarities, variation_names)


def main():
    gold_service_ids = pd.read_csv(GOLD_SERVICES_PATH)['id']

    config_files = glob.glob(CONFIG_DIR + '*')
    print("Config files given:")
    print(config_files)

    # We first generate the recommendations for all the configs given
    for config_file in tqdm(config_files):
        update_backend_settings(config_file)
        structures_update()

        store_recommendations(gold_service_ids, RECOMMENDATIONS_STORE_DIR + config_file.split('/')[-1][:-5] + '.csv')

    # Then we compare their distance
    find_dissimilar_variations(RECOMMENDATIONS_STORE_DIR, difference_of_sets)

    # TODO: Store plots


if __name__ == '__main__':
    main()
