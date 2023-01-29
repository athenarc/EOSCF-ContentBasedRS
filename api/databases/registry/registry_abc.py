from abc import ABC, abstractmethod


class Registry(ABC):
    def get_services_by_ids(self, ids, **kwargs):
        return []

    def get_services(self, **kwargs):
        return []

    def get_non_published_services(self):
        return []

    def get_service(self, service_id, **kwargs):
        return None

    def get_projects(self):
        return []

    def get_project(self, project_id):
        return None

    def get_project_services(self, project_id):
        return []

    def get_users(self, **kwargs):
        return []

    def get_user_services(self, user_id):
        return []

    def get_scientific_domains(self):
        return []

    def get_categories(self):
        return []

    def get_target_users(self):
        return []

    def _remove_general_attributes_from_services(self, services):
        return []

    def _remove_general_attributes_from_single_service(self, service):
        return None

    def is_valid_service(self, service_id):
        return False

    def is_valid_project(self, project_id):
        return False

    def is_valid_user(self, user_id):
        return False
