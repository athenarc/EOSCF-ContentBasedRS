from app.recommender.project_completion.initialization import association_rules
from app.recommender.update.update import Update


class ProjectCompletionUpdate(Update):
    def initialize(self):
        association_rules.initialize_association_rules()

    def update(self):
        association_rules.create_association_rules()

    def update_for_new_service(self, service_id: int):
        pass

    def revert(self):
        association_rules.delete_association_rules()
