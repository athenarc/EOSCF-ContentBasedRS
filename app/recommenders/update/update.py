from abc import ABC, abstractmethod

from app.exceptions import NoneProjects, NoneServices


class Update(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def update_for_new_service(self, service_id: int):
        pass

    @abstractmethod
    def revert(self):
        pass


class AggregatedUpdate:
    def __init__(self, updaters: list[Update]):
        """

        Args:
            updaters: List of objects that perform use case updating
        """
        self.updaters = updaters

    def initialize(self):
        try:
            for updater in self.updaters:
                updater.initialize()
        except (NoneServices, NoneProjects) as e:
            for updater in self.updaters:
                updater.revert()
            raise e

    def update(self):
        try:
            for updater in self.updaters:
                updater.update()
        except (NoneServices, NoneProjects) as e:
            for updater in self.updaters:
                updater.revert()
            raise e

    def update_for_new_service(self, service_id: int):
        for updater in self.updaters:
            updater.update_for_new_service(service_id)
