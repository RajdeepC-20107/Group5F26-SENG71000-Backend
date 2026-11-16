from fastapi.testclient import TestClient

# For now the assumption is that a user with user_id of 1 is present with at least one score
# A user with user_id of 2 is present with no scores
# No user exists with user_id -1
# TODO: make staging with predefined entries


def test_get_scores(client: TestClient):
    response = client.get("/users/1/scores")
    assert response.status_code == 200

    scores = response.json()
    assert len(scores) > 0
    assert scores[0]["Tracks"] is not None
    assert isinstance(scores[0]['Tracks']['track_object'], str)


def test_get_scores_nonexistent_user(client: TestClient):
    response = client.get("/users/-1/scores")
    assert response.status_code == 404


def test_get_scores_nothing_graded(client: TestClient):
    response = client.get("/users/2/scores")
    assert response.status_code == 200

    scores = response.json()
    assert len(scores) == 0
