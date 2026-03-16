import pytest
import uuid
import allure

from api import MockApiClient


def _user_payload() -> dict:
    """Unique payload for each call."""
    uid = uuid.uuid4().hex[:8]
    return {
        "name": f"Alice Smith {uid}",
        "username": f"alicesmith_{uid}",
        "email": f"alice_{uid}@example.com",
    }


@allure.suite("Users API")
class TestGetUsers:
    @allure.title("GET /users - status 200")
    @pytest.mark.smoke
    def test_get_users_status(self, api_client: MockApiClient):
        response = api_client.get_users()
        assert response.status_code == 200

    @allure.title("GET /users - body is a list")
    def test_get_users_returns_list(self, api_client: MockApiClient):
        response = api_client.get_users()
        assert isinstance(api_client.data(response), list)

    @allure.title("GET /users - list is not empty")
    def test_get_users_not_empty(self, api_client: MockApiClient):
        response = api_client.get_users()
        assert len(api_client.data(response)) > 0

    @allure.title("GET /users - has 'pagination' field")
    def test_get_users_has_pagination(self, api_client: MockApiClient):
        response = api_client.get_users()
        pagination = api_client.pagination(response)
        assert pagination is not None
        assert "total" in pagination
        assert "page" in pagination
        assert "limit" in pagination
        assert "totalPages" in pagination
        assert "hasNext" in pagination
        assert "hasPrev" in pagination

    @allure.title("GET /users/{id} - status 200")
    @pytest.mark.smoke
    def test_get_user_by_id_status(self, api_client: MockApiClient):
        response = api_client.get_user(1)
        assert response.status_code == 200

    @allure.title("GET /users/{id} - returns correct ID")
    def test_get_user_by_id_correct_id(self, api_client: MockApiClient):
        response = api_client.get_user(1)
        assert api_client.data(response)["id"] == 1

    @allure.title("GET /users/{id} - user has required fields")
    def test_get_user_has_required_fields(self, api_client: MockApiClient):
        response = api_client.get_user(1)
        user = api_client.data(response)
        for field in ("id", "name", "username", "email"):
            assert field in user, f"Missing field: {field}"

    @allure.title("GET /users/{id} - unavailable ID returns 404")
    def test_get_user_not_found(self, api_client: MockApiClient):
        response = api_client.get_user(99999)
        assert response.status_code == 404


@allure.suite("Users API")
class TestCreateUser:
    @allure.title("POST /users - status 201")
    @pytest.mark.smoke
    def test_create_user_status(self, api_client: MockApiClient):
        response = api_client.create_user(_user_payload())
        assert response.status_code == 201

    @allure.title("POST /users - response has all created fields")
    def test_create_user_returns_data(self, api_client: MockApiClient):
        payload = _user_payload()
        response = api_client.create_user(payload)
        user = api_client.data(response)
        assert user["name"] == payload["name"]
        assert user["username"] == payload["username"]
        assert user["email"] == payload["email"]

    @allure.title("POST /users - response has ID")
    def test_create_user_has_id(self, api_client: MockApiClient):
        response = api_client.create_user(_user_payload())
        assert "id" in api_client.data(response)


@allure.suite("Users API")
class TestUpdateUser:
    @allure.title("PUT /users/{id} - status 200")
    def test_update_user_status(self, api_client: MockApiClient, created_user: dict):
        uid = uuid.uuid4().hex[:8]
        response = api_client.update_user(
            created_user["id"],
            {
                "name": f"Updated Name {uid}",
                "username": f"updated_{uid}",
                "email": f"updated_{uid}@example.com",
            },
        )
        assert response.status_code == 200

    @allure.title("PUT /users/{id} - data updated")
    def test_update_user_data_changed(
        self, api_client: MockApiClient, created_user: dict
    ):
        uid = uuid.uuid4().hex[:8]
        new_name = f"Updated Name {uid}"
        response = api_client.update_user(
            created_user["id"],
            {
                "name": new_name,
                "username": created_user["username"],
                "email": created_user["email"],
            },
        )
        assert api_client.data(response)["name"] == new_name


@allure.suite("Users API")
class TestDeleteUser:
    @allure.title("DELETE /users/{id} - status 200 / 204")
    @pytest.mark.smoke
    def test_delete_user_status(self, api_client: MockApiClient, created_user: dict):
        response = api_client.delete_user(created_user["id"])
        assert response.status_code == 204

    @allure.title("DELETE /users/{id} — response body is empty")
    def test_delete_user_empty_body(
        self, api_client: MockApiClient, created_user: dict
    ):
        response = api_client.delete_user(created_user["id"])
        assert response.content == b""
