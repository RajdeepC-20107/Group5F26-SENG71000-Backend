from fastapi.testclient import TestClient

# A user with a username sfterefe and driver's licence T-1234-56789-40405 identified by password123 should exist
# Passwords are case-sensitive


def test_login_username(client: TestClient):
    response = client.post(
        "/login",
        json={"identifier": "sfterefe", "password": "password123"}
    )
    assert response.status_code == 200


def test_login_drivers_licence(client: TestClient):
    response = client.post(
        "/login",
        json={"identifier": "T-1234-56789-40405", "password": "password123"}
    )
    assert response.status_code == 200


def test_login_incorrect_id(client: TestClient):
    response1 = client.post(
        "/login",
        json={"identifier": "unkn0wn", "password": "password123"}
    )

    response2 = client.post(
        "/login",
        json={"identifier": "sfterefe", "password": "P@ssw0rd123!"}
    )

    response3 = client.post(
        "/login",
        json={"identifier": "unkn0wn", "password": "P@ssw0rd123!"}
    )

    response4 = client.post(
        "/login",
        json={"identifier": "", "password": "password123"}
    )

    response5 = client.post(
        "/login",
        json={"identifier": "", "password": ""}
    )

    response6 = client.post(
        "/login",
        json={"identifier": "sfterefe", "password": ""}
    )

    response7 = client.post(
        "/login",
        json={"identifier": "SftErefE", "password": "Password123"}
    )

    assert response1.status_code == 401
    assert response2.status_code == 401
    assert response3.status_code == 401
    assert response4.status_code == 401
    assert response5.status_code == 401
    assert response6.status_code == 401
    assert response7.status_code == 401
