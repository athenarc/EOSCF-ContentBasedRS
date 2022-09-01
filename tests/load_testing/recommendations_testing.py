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
                elif response.json() != [
                    {
                        "service_id": 3,
                        "score": 0.5168381140137174
                    },
                    {
                        "service_id": 2,
                        "score": 0.48237195514438336
                    },
                    {
                        "service_id": 57,
                        "score": 0.40898855358687314
                    },
                    {
                        "service_id": 177,
                        "score": 0.40001248730878636
                    },
                    {
                        "service_id": 42,
                        "score": 0.3981655988957545
                    }
                ]:
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
                elif response.json():
                    response.failure("Did not get expected recommended services")
            except JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
