import pytest
import requests

BASE_URL = "http://0.0.0.0:4559/v1"


@pytest.mark.api
@pytest.mark.rs_mongo
def test_rs_health():
    r = requests.get(url=f"{BASE_URL}/health")
    assert r.status_code == 200


@pytest.mark.api
@pytest.mark.rs_mongo
def test_rs_update():
    r = requests.get(url=f"{BASE_URL}/update")
    assert r.status_code == 200


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("registered_user_rs_mongo")
def test_rs_registered_user_rs_mongo_status(registered_user_rs_mongo):
    r = requests.post(url=f"{BASE_URL}/similar_services/recommendation",
                      json=registered_user_rs_mongo['request'])

    assert r.status_code == 200


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("anonymous_user_rs_mongo")
def test_rs_anonymous_user_rs_mongo_status(anonymous_user_rs_mongo):
    r = requests.post(url=f"{BASE_URL}/similar_services/recommendation",
                      json=anonymous_user_rs_mongo['request'])

    assert r.status_code == 200


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("registered_user_rs_mongo")
def test_rs_registered_user_rs_mongo_response_length(registered_user_rs_mongo):
    registered_user_rs_mongo['request']['num'] = 3
    r = requests.post(url=f"{BASE_URL}/similar_services/recommendation",
                      json=registered_user_rs_mongo['request'])

    assert len(r.json()['recommendations']) == 3
    assert len(r.json()['explanations']) == 3
    assert len(r.json()['explanations_short']) == 3
    assert len(r.json()['scores']) == 3


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("anonymous_user_rs_mongo")
def test_rs_anonymous_user_rs_mongo_response_length(anonymous_user_rs_mongo):
    anonymous_user_rs_mongo['request']['num'] = 3
    r = requests.post(url=f"{BASE_URL}/similar_services/recommendation",
                      json=anonymous_user_rs_mongo['request'])

    assert len(r.json()['recommendations']) == 3
    assert len(r.json()['explanations']) == 3
    assert len(r.json()['explanations_short']) == 3
    assert len(r.json()['scores']) == 3


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("registered_user_rs_mongo")
@pytest.mark.xfail(reason='Fixture is not kept updated')
def test_rs_registered_user_rs_mongo_check_returned_recs(registered_user_rs_mongo):
    r = requests.post(url=f"{BASE_URL}/similar_services/recommendation",
                      json=registered_user_rs_mongo['request'])

    assert r.json()['recommendations'] == registered_user_rs_mongo['expected_response']['recommendations']


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("anonymous_user_rs_mongo")
@pytest.mark.xfail(reason='Fixture is not kept updated')
def test_rs_anonymous_user_rs_mongo_check_returned_recs(anonymous_user_rs_mongo):
    r = requests.post(url=f"{BASE_URL}/similar_services/recommendation",
                      json=anonymous_user_rs_mongo['request'])

    assert r.json()['recommendations'] == anonymous_user_rs_mongo['expected_response']['recommendations']


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("registered_user_rs_mongo")
@pytest.mark.xfail(reason='Fixture is not kept updated')
def test_rs_registered_user_rs_mongo_check_returned_scores(registered_user_rs_mongo):
    r = requests.post(url=f"{BASE_URL}/similar_services/recommendation",
                      json=registered_user_rs_mongo['request'])

    assert r.json()['scores'] == registered_user_rs_mongo['expected_response']['scores']


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("anonymous_user_rs_mongo")
@pytest.mark.xfail(reason='Fixture is not kept updated')
def test_rs_anonymous_user_rs_mongo_check_returned_scores(anonymous_user_rs_mongo):
    r = requests.post(url=f"{BASE_URL}/similar_services/recommendation",
                      json=anonymous_user_rs_mongo['request'])

    assert r.json()['scores'] == anonymous_user_rs_mongo['expected_response']['scores']


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("anonymous_user_rs_mongo")
def test_rs_anonymous_user_rs_mongo_check_returned_panel_id(anonymous_user_rs_mongo):
    r = requests.post(url=f"{BASE_URL}/similar_services/recommendation",
                      json=anonymous_user_rs_mongo['request'])

    assert r.json()['panel_id'] == anonymous_user_rs_mongo['expected_response']['panel_id']


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("anonymous_user_rs_mongo")
def test_rs_anonymous_user_rs_mongo_check_returned_engine_version(anonymous_user_rs_mongo):
    r = requests.post(url=f"{BASE_URL}/similar_services/recommendation",
                      json=anonymous_user_rs_mongo['request'])

    assert r.json()['engine_version'] == anonymous_user_rs_mongo['expected_response']['engine_version']


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("anonymous_user_rs_mongo")
def test_rs_anonymous_user_rs_mongo_check_explanation(anonymous_user_rs_mongo):
    r = requests.post(url=f"{BASE_URL}/similar_services/recommendation",
                      json=anonymous_user_rs_mongo['request'])

    assert r.json()['explanations'][0] \
           == anonymous_user_rs_mongo['expected_response']['explanations'][0]


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("anonymous_user_rs_mongo")
def test_rs_anonymous_user_rs_mongo_check_short_explanation(anonymous_user_rs_mongo):
    r = requests.post(url=f"{BASE_URL}/similar_services/recommendation",
                      json=anonymous_user_rs_mongo['request'])

    assert r.json()['explanations_short'][0] \
           == anonymous_user_rs_mongo['expected_response']['explanations_short'][0]


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("completed_project_empty")
def test_rs_project_completion_status(completed_project_empty):
    r = requests.post(url=f"{BASE_URL}/project_completion/recommendation",
                      json=completed_project_empty['request'])

    assert r.status_code == 200


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("completed_project_empty")
def test_rs_project_completion_check_panel_id(completed_project_empty):
    r = requests.post(url=f"{BASE_URL}/project_completion/recommendation",
                      json=completed_project_empty['request'])

    assert r.json()['panel_id'] == completed_project_empty['expected_response']['panel_id']


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("completed_project_empty")
def test_rs_project_completion_check_engine_version(completed_project_empty):
    r = requests.post(url=f"{BASE_URL}/project_completion/recommendation",
                      json=completed_project_empty['request'])

    assert r.json()['engine_version'] == completed_project_empty['expected_response']['engine_version']


@pytest.mark.api
@pytest.mark.rs_mongo
def test_project_assistant_response_status():
    r = requests.post(url=f"{BASE_URL}/project_assistant/recommendation",
                      json={"prompt": "I want a service to visualize my data", "max_num": 5})

    assert r.status_code == 200


@pytest.mark.api
@pytest.mark.rs_mongo
def test_project_assistant_response_length():
    r = requests.post(url=f"{BASE_URL}/project_assistant/recommendation",
                      json={"prompt": "I want a service to visualize my data", "max_num": 3})

    assert len(r.json()['recommendations']) == 3
    assert len(r.json()['explanations']) == 3
    assert len(r.json()['explanations_short']) == 3
    assert len(r.json()['score']) == 3


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("project_assistant")
@pytest.mark.xfail(reason='Fixture is not kept updated')
def test_project_assistant_returned_recs(project_assistant):
    r = requests.post(url=f"{BASE_URL}/project_assistant/recommendation",
                      json=project_assistant["request"])

    assert r.json()['recommendations'] == project_assistant['expected_response']['recommendations']


@pytest.mark.api
@pytest.mark.rs_mongo
@pytest.mark.usefixtures("project_assistant")
@pytest.mark.xfail(reason='Fixture is not kept updated')
def test_project_assistant_returned_scores(project_assistant):
    r = requests.post(url=f"{BASE_URL}/project_assistant/recommendation",
                      json=project_assistant["request"])

    assert r.json()['score'] == project_assistant['expected_response']['score']
