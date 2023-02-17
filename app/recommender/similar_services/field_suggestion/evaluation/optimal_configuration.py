import itertools
import json

from app.recommender.similar_services.field_suggestion.evaluation.evaluation import \
    evaluation
from tqdm import tqdm


def optimal_config(configs_results, metric, per_field=True):
    if per_field:
        opt_config = {}
        # Find the optimal configuration for each field
        for field in list(configs_results.values())[0]["per_field"].keys():
            # Get all metric's results for the current field
            field_metric_results = dict(
                map(lambda config: (config[0], config[1]["per_field"][field][metric]),
                    configs_results.items())
            )
            opt_config[field] = max(field_metric_results, key=field_metric_results.get)
        return opt_config
    else:
        metric_configs_results = dict(map(lambda config: (config[0], config[1][metric]), configs_results.items()))
        return max(metric_configs_results, key=metric_configs_results.get)


def find_optimal_configuration(metric="precision", per_field=True):
    """
    Search multiple combinations of configuration parameters values and returns the optimal one based on the requested
    metric
    @param metric: 'precision' | 'recall' | 'f1_score'
    @return:
    """
    similarity_threshold_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    considered_services_threshold_values = [5, 10, 15]
    frequency_threshold_values = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    maximum_recommendation_values = [1, 3, 5]

    # Initialize different configuration settings
    configs = list(itertools.product(*[
        similarity_threshold_values,
        considered_services_threshold_values,
        frequency_threshold_values,
        maximum_recommendation_values
    ]))

    # Get the evaluation results for every configuration
    configs_results = {}
    for config in tqdm(configs):
        config_results = evaluation(similarity_threshold=config[0], considered_services_threshold=config[1],
                                    frequency_threshold=config[2], maximum_suggestions=config[3])

        # For every metric average the results from all fields
        metrics = ["precision", "recall", "f1_score"]

        configs_results[config] = {}  # Stores the average result of a metric for all fields
        for m in metrics:
            configs_results[config][m] = sum([field_results[m] for field_results in config_results.values()]) / \
                                         len(config_results)

        configs_results[config].update({"per_field": config_results})

    # Save all results
    with open("api/recommender/similar_services/field_suggestion/evaluation/results/evaluations_results.json", "w") as outfile:
        json.dump({str(k): v for k, v in configs_results.items()}, outfile)

    return optimal_config(configs_results, metric, per_field)


if __name__ == '__main__':
    optimal_settings_per_field = find_optimal_configuration(metric='f1_score', per_field=True)

    for field, optimal_settings in optimal_settings_per_field.items():
        print(
            f"Optimal settings for {field}: similarity_threshold={optimal_settings[0]}, "
            f"considered_services_threshold={optimal_settings[1]},"
            f"frequency_threshold={optimal_settings[2]}",
            f"maximum_suggestions={optimal_settings[3]}"
        )
