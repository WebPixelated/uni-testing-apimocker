import pytest
import uuid
import time
import allure

from api import MockApiClient
from helpers import random_email_local, random_name, random_username


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

    # @allure.title("GET /users - has 'pagination' field")
    # def test_get_users_has_pagination(self, api_client: MockApiClient):
    #     response = api_client.get_users()
    #     pagination = api_client.pagination(response)
    #     assert pagination is not None
    #     assert "total" in pagination
    #     assert "page" in pagination
    #     assert "limit" in pagination
    #     assert "totalPages" in pagination
    #     assert "hasNext" in pagination
    #     assert "hasPrev" in pagination

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

    @allure.title("POST /users - minimum length values")
    def test_create_user_min_length(self, api_client: MockApiClient):
        payload = {
            "name": random_name(1),
            "username": random_username(3),
            "email": f"{random_email_local(1)}@{random_email_local(1)}.co",
        }
        response = api_client.create_user(payload)
        assert response.status_code == 201

    @allure.title("POST /users - maximum length values")
    def test_create_user_max_length(self, api_client: MockApiClient):
        payload = {
            "name": random_name(100),
            "username": random_username(50),
            "email": f"{random_email_local(40)}@example.com",
        }
        response = api_client.create_user(payload)
        assert response.status_code == 201

    @allure.title("POST /users - Unicode / Emojis in name")
    def test_create_user_unicode_name(self, api_client: MockApiClient):
        payload = _user_payload()
        payload["name"] = f"{random_name(10)} 🧑‍💻"
        response = api_client.create_user(payload)
        assert response.status_code == 201

    @allure.title("POST /users - response has ID")
    def test_create_user_has_id(self, api_client: MockApiClient):
        response = api_client.create_user(_user_payload())
        assert "id" in api_client.data(response)

    @allure.title("POST /users - empty body")
    def test_create_user_empty_body(self, api_client: MockApiClient):
        response = api_client.create_user({})
        assert response.status_code == 400
        error_data = response.json()
        assert error_data.get("error") == "Validation Error"

    @allure.title("POST /users - missing required fields")
    @pytest.mark.parametrize("missing_field", ["name", "username", "email"])
    def test_create_user_missing_fields(
        self, api_client: MockApiClient, missing_field: str
    ):
        payload = _user_payload()
        payload.pop(missing_field)
        response = api_client.create_user(payload)
        assert response.status_code == 400
        error_data = response.json()
        assert any(
            d.get("path") == missing_field for d in error_data.get("details", [])
        )

    @allure.title("POST /users - invalid email format")
    def test_create_user_invalid_email(self, api_client: MockApiClient):
        payload = _user_payload()
        payload["email"] = "invalid-email-format"
        response = api_client.create_user(payload)
        assert response.status_code == 400
        error_data = response.json()
        assert any(d.get("path") == "email" for d in error_data.get("details", []))

    @allure.title("POST /users - name exceeds max length (100 chars)")
    def test_create_user_name_too_long(self, api_client: MockApiClient):
        payload = _user_payload()
        payload["name"] = "A" * 101
        response = api_client.create_user(payload)
        assert response.status_code == 400

    @allure.title("POST /users - username too short (under 3 chars)")
    def test_create_user_username_too_short(self, api_client: MockApiClient):
        payload = _user_payload()
        payload["username"] = "ab"
        response = api_client.create_user(payload)
        assert response.status_code == 400

    @allure.title("POST /users - username invalid chars / SQLi / XSS")
    @pytest.mark.parametrize(
        "invalid_username",
        ["user name", "<script>alert(1)</script>", "' OR '1'='1", "user@name"],
    )
    def test_create_user_username_invalid_chars(
        self, api_client: MockApiClient, invalid_username: str
    ):
        payload = _user_payload()
        payload["username"] = invalid_username
        response = api_client.create_user(payload)
        assert response.status_code == 400
        error_data = response.json()
        assert any(d.get("path") == "username" for d in error_data.get("details", []))

    @allure.title("POST /users - extra non-existent fields")
    def test_create_user_extra_fields(self, api_client: MockApiClient):
        payload = _user_payload()
        payload["role"] = "superadmin"
        response = api_client.create_user(payload)
        assert response.status_code in (201, 400)

    @allure.title("POST /users - unsupported Content-Type")
    def test_create_user_unsupported_content_type(self, api_client: MockApiClient):
        url = api_client._url("/users")
        response = api_client.session.post(
            url, data="not json", headers={"Content-Type": "text/plain"}
        )
        assert response.status_code in (400, 415)


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
class TestPatchUser:
    @allure.title("PATCH /users/{id} - successfully update single field")
    @pytest.mark.xfail(
        reason="Bug on apimocker.com: PATCH /users/:id returns 404 despite documentation"
    )
    def test_patch_user_name(self, api_client: MockApiClient, created_user: dict):
        new_name = f"Patched {uuid.uuid4().hex[:8]}"
        response = api_client.patch_user(created_user["id"], {"name": new_name})

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. Bug in API?"
        )
        user = api_client.data(response)
        assert user["name"] == new_name
        assert user["username"] == created_user["username"]  # Unchanged
        assert user["email"] == created_user["email"]  # Unchanged


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


@allure.suite("Users API - Search & Advanced Features")
class TestAdvancedUsersFeatures:
    @allure.title("GET /users?_delay=2000 - response delay simulation")
    def test_users_delay(self, api_client: MockApiClient):
        start_time = time.time()
        response = api_client.get_users(params={"_delay": 2000})
        end_time = time.time()
        assert response.status_code == 200
        elapsed_ms = (end_time - start_time) * 1000
        assert elapsed_ms >= 1900, "Response should be delayed by ~2000ms"

    @allure.title("GET /error/404 - simulate 404 error endpoint")
    def test_simulate_404_error(self, api_client: MockApiClient):
        response = api_client.get_error(404)
        assert response.status_code == 404
