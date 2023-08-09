import random
from collections import OrderedDict

from app.databases.registry.registry_selector import get_registry


class RerankingSurveyModel:
    def __init__(self, viewed_service_id, services_per_diversity, total_candidates):
        self.viewed_service_id = viewed_service_id
        self.services_per_diversity = services_per_diversity
        self.total_candidate = total_candidates

        self.name, self.tagline, self.description, self.scientific_domains, self.categories \
            = self.populate_viewed_service_info(viewed_service_id)

    def deduplication(self):
        """
        Diversity weight change might not always cause a change in the recommended services.
        In case of a duplicate recommendation we keep the one with the smallest diversity.
        """
        deduplicated_services_per_diversity = {}
        duplicate_pairs = []
        for diversity, rec_services in self.services_per_diversity.items():
            checked_diversities = [cand_diversity for cand_diversity in self.services_per_diversity.keys()
                                   if cand_diversity < diversity]

            rec_services_set = set(rec_services)

            exists = False
            for checked_diversity in checked_diversities:
                if set(self.services_per_diversity[checked_diversity]) == rec_services_set:
                    exists = True
                    duplicate_pairs.append((checked_diversity, diversity))
            if not exists:
                deduplicated_services_per_diversity[diversity] = rec_services

        return deduplicated_services_per_diversity, duplicate_pairs

    @staticmethod
    def populate_viewed_service_info(viewed_service_id):
        db = get_registry()
        service = db.get_service(viewed_service_id, remove_generic_attributes=False)
        scientific_domains = ", ".join([db.get_specific_scientific_domain_name(domain_id)
                                        for domain_id in service["scientific_domains"]])
        categories = ", ".join([db.get_specific_category_name(category_id)
                                for category_id in service["categories"]])

        return service["name"], service["tagline"], service["description"], scientific_domains, categories

    @staticmethod
    def get_rec_service_info(rec_service_id):
        db = get_registry()
        service = db.get_service(rec_service_id, remove_generic_attributes=False)

        return service["name"], service["tagline"]

    def shuffle_diversities_order(self):
        diversity_inds = self.services_per_diversity.keys()  # This will change depending on deduplication
        shuffle_order = random.sample(diversity_inds, len(diversity_inds))

        return shuffle_order

    def get_recommendation_sets(self, div_shuffled_order):
        recommendation_sets = {}
        for ind, diversity in enumerate(div_shuffled_order, start=1):
            recommendations = self.services_per_diversity[diversity]
            recommendation_sets[f"set{ind}"] = OrderedDict()
            for rec_id in recommendations:
                name, tagline = self.get_rec_service_info(rec_id)
                recommendation_sets[f"set{ind}"][name] = tagline

        # Add empty recommendations to reach the total number of diversity variations
        for ind in range(len(div_shuffled_order) + 1, self.total_candidate + 1):
            recommendation_sets[f"set{ind}"] = self.ret_empty_rec_values()

        return recommendation_sets

    @staticmethod
    def ret_empty_rec_values():
        return {"": ""}

    def to_dict(self, deduplication=True):
        if deduplication:
            self.services_per_diversity, duplicate_pairs = self.deduplication()
        else:
            duplicate_pairs = []

        viewed_service_info = {
            "name": self.name,
            "tagline": self.tagline,
            "description": self.description,
            "scientific_domains": self.scientific_domains,
            "categories": self.categories,
        }

        shuffled_diversities = self.shuffle_diversities_order()
        recommendation_sets = self.get_recommendation_sets(shuffled_diversities)
        shuffling_info = {
            "shuffled_diversities": shuffled_diversities,
            "duplicate_pairs": duplicate_pairs
        }
        choices = {
            "variants": [
                {"value": f"Set {ind + 1}"} for ind in range(len(shuffled_diversities))
            ]
        }

        return viewed_service_info | recommendation_sets | shuffling_info | choices
