import pandas as pd
import numpy as np
import json


def select_services_with_poor_recommendations(recommendations_ratings, num=10):
    # Get recommendations sets with only irrelevant services
    poor_recommendations = recommendations_ratings[recommendations_ratings.sum(axis=1) == 0]
    return list(poor_recommendations.head(num).index)


def select_services_with_good_recommendations(recommendations_ratings, num=10):
    # Get recommendations sets with only relevant services
    rec_set_len = len(recommendations_ratings.columns)
    good_recommendations = recommendations_ratings[recommendations_ratings.sum(axis=1) == rec_set_len]
    return list(good_recommendations.head(num).index)


if __name__ == '__main__':
    # Read csv with the manual evaluation results
    results = pd.read_csv(
        "./api/recommender/similar_services/service_recommendation/evaluation/results/manual_evaluation_250.csv",
        header=[0, 1, 2])

    # Add ids of the services as index
    with open("./api/recommender/similar_services/service_recommendation/evaluation/results/evaluated_services.json") as f:
        ids = np.array(json.load(f))

    # Keep the relevance result of each recommended service
    results = results.iloc[:, [3, 5, 7, 9, 11, 13, 15]]
    # Rename columns
    results.columns = [1, 2, 3, 4, 5, 6, "better_choices"]

    # Remove services with None id
    none_indices = np.where(ids == "")[0]
    ids = np.delete(ids, none_indices)
    results = results.drop(none_indices)

    results = results.set_index(ids)
    # Convert all values to int. Missing values(-) => Nan
    for column in [1, 2, 3, 4, 5, 6]:
        results[column] = pd.to_numeric(results[column], errors='coerce')

    tricky_services = list(results[results["better_choices"].notnull()].index)

    challenging_services = select_services_with_poor_recommendations(results[[1, 2, 3, 4, 5, 6]])
    non_challenging_services = select_services_with_good_recommendations(results[[1, 2, 3, 4, 5, 6]])

    selected_services = set(tricky_services + challenging_services + non_challenging_services)
    print(f"challenging services: {challenging_services}\nnon challenging services: {non_challenging_services}\n"
          f"tricky services: {tricky_services}")

