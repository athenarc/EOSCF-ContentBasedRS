from app.recommender.project_completion.components.filtering import filtering
from app.recommender.project_completion.initialization.association_rules import \
    get_association_rules


def get_recommendation_candidates(project_services):
    # TODO: if the recommendations are not enough search with subsets of project services?
    rules = get_association_rules()

    # Get all the consequents of project's services set
    recommendations = [{"service_id": service_id, "score": 1}
                       for service_id in list(set().union(*rules[rules.apply(lambda row: project_services == list(row["antecedents"]), axis=1)]["consequents"].values))]

    recommendations = filtering(recommendations)
    return recommendations
