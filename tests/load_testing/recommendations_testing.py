from json import JSONDecodeError

from locust import HttpUser, between, task


class BrowsingServicesUser(HttpUser):
    # We assume that a user will change service page (requesting recommendations) every 5 to 15 seconds
    wait_time = between(5, 15)
    weight = 8

    @task
    def get_similar_service(self):
        with self.client.post("/similar_services/recommendation",
                              json={
                                  "user_id": 1,
                                  "service_id": 1,
                                  "num": 5
                              },
                              catch_response=True) \
                as response:
            try:
                if response.status_code == 500:
                    response.failure("Internal server error")
                elif response.json() != {
                    "panel_id": "similar_services",
                    "recommendations": [
                        3,
                        2,
                        57,
                        177,
                        42
                    ],
                    "explanations": [
                        "Based on the metadata and the text attributes we retrieve the services "
                        "that are most similar to the one you are currently viewing.",
                        "Based on the metadata and the text attributes we retrieve the services "
                        "that are most similar to the one you are currently viewing.",
                        "Based on the metadata and the text attributes we retrieve the services "
                        "that are most similar to the one you are currently viewing.",
                        "Based on the metadata and the text attributes we retrieve the services "
                        "that are most similar to the one you are currently viewing.",
                        "Based on the metadata and the text attributes we retrieve the services "
                        "that are most similar to the one you are currently viewing."
                    ],
                    "explanations_short": [
                        "Similar metadata and text to the service you are viewing",
                        "Similar metadata and text to the service you are viewing",
                        "Similar metadata and text to the service you are viewing",
                        "Similar metadata and text to the service you are viewing",
                        "Similar metadata and text to the service you are viewing"
                    ],
                    "score": [
                        0.5168381140137174,
                        0.48237195514438336,
                        0.40898855358687314,
                        0.40001248730878636,
                        0.3981655988957545
                    ],
                    "engine_version": "v1"
                }:
                    response.failure("Did not get expected recommended services")
            except JSONDecodeError:
                # response.failure(f"Response \"{response}\" could not be decoded as JSON")
                raise ValueError(f"Response \"{response.content}\" could not be decoded as JSON")


class ProjectEditingUser(HttpUser):
    # We assume that a user will change service page (requesting recommendations) every 1 to 5 seconds
    wait_time = between(10, 30)
    weight = 1

    @task
    def get_project_completion(self):
        with self.client.post("/project_completion/recommendation",
                              json={
                                  "project_id": 1,
                                  "num": 5
                              },
                              catch_response=True) \
                as response:
            try:
                if response.status_code == 500:
                    response.failure("Internal server error")
                elif response.json() != {
                    "panel_id": "project_completion",
                    "recommendations": [],
                    "explanations": [],
                    "explanations_short": [],
                    "score": [],
                    "engine_version": "v1"
                }:
                    response.failure("Did not get expected recommended services")
            except JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
