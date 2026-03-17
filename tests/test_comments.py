import uuid
import pytest
import allure

from api.mock_api_client import MockApiClient
from helpers import random_name


def _comment_payload() -> dict:
    uid = uuid.uuid4().hex[:8]
    return {
        "name": f"Commenter {uid}",
        "email": f"commenter_{uid}@example.com",
        "body": f"Test comment body {uid}",
        "postId": 1,
    }


@allure.suite("Comments API")
class TestGetComments:
    @allure.title("GET /comments - status 200")
    @pytest.mark.smoke
    def test_get_comments_status(self, api_client: MockApiClient):
        response = api_client.get_comments()
        assert response.status_code == 200

    @allure.title("GET /comments - body is a list")
    def test_get_comments_returns_list(self, api_client: MockApiClient):
        response = api_client.get_comments()
        assert isinstance(api_client.data(response), list)

    @allure.title("GET /comments - list is not empty")
    def test_get_comments_not_empty(self, api_client: MockApiClient):
        response = api_client.get_comments()
        assert len(api_client.data(response)) > 0

    @allure.title("GET /comments - has 'pagination' field")
    def test_get_comments_has_pagination(self, api_client: MockApiClient):
        response = api_client.get_comments()
        pagination = api_client.pagination(response)
        assert pagination is not None
        assert "total" in pagination
        assert "totalPages" in pagination

    @allure.title("GET /comments/{id} - status 200")
    @pytest.mark.smoke
    def test_get_comment_by_id_status(self, api_client: MockApiClient):
        response = api_client.get_comment(1)
        assert response.status_code == 200

    @allure.title("GET /comments/{id} - comment has required fields")
    def test_get_comment_has_required_fields(self, api_client: MockApiClient):
        comment = api_client.data(api_client.get_comment(1))
        for field in ("id", "name", "email", "body", "postId"):
            assert field in comment, f"Missing field: {field}"

    @allure.title("GET /comments/{id} - has inner 'post' object")
    def test_get_comment_has_nested_post(self, api_client: MockApiClient):
        comment = api_client.data(api_client.get_comment(1))
        assert "post" in comment
        assert "id" in comment["post"]
        assert "title" in comment["post"]

    @allure.title("GET /comments/{id} - unavailable ID returns 404")
    def test_get_comment_not_found(self, api_client: MockApiClient):
        response = api_client.get_comment(99999)
        assert response.status_code == 404


@allure.suite("Comments API")
class TestCreateComment:
    @allure.title("POST /comments - status 201")
    @pytest.mark.smoke
    def test_create_comment_status(self, api_client: MockApiClient):
        response = api_client.create_comment(_comment_payload())
        assert response.status_code == 201

    @allure.title("POST /comments - comment has payload fields")
    def test_create_comment_returns_data(self, api_client: MockApiClient):
        payload = _comment_payload()
        response = api_client.create_comment(payload)
        comment = api_client.data(response)
        assert comment["name"] == payload["name"]
        assert comment["email"] == payload["email"]
        assert comment["body"] == payload["body"]
        assert comment["postId"] == payload["postId"]

    @allure.title("POST /comments - todo has ID")
    def test_create_comment_has_id(self, api_client: MockApiClient):
        response = api_client.create_comment(_comment_payload())
        assert "id" in api_client.data(response)

    @allure.title("POST /comments - invalid email")
    def test_create_comment_invalid_email(self, api_client: MockApiClient):
        payload = _comment_payload()
        payload["email"] = "invalid-email-format"
        response = api_client.create_comment(payload)
        assert response.status_code == 400
        assert any(d.get("path") == "email" for d in response.json().get("details", []))

    @allure.title("POST /comments - invalid postId (negative integer)")
    def test_create_comment_invalid_post_id(self, api_client: MockApiClient):
        payload = _comment_payload()
        payload["postId"] = -5
        response = api_client.create_comment(payload)
        assert response.status_code == 400
        assert any(
            d.get("path") == "postId" for d in response.json().get("details", [])
        )

    @allure.title("POST /comments - body exceeds max length (1000 chars)")
    def test_create_comment_body_too_long(self, api_client: MockApiClient):
        payload = _comment_payload()
        payload["body"] = random_name(1001)
        response = api_client.create_comment(payload)
        assert response.status_code == 400


@allure.suite("Comments API")
class TestUpdateComment:
    @allure.title("PUT /comments/{id} - status 200")
    def test_update_comment_status(
        self, api_client: MockApiClient, created_comment: dict
    ):
        payload = _comment_payload()
        response = api_client.update_comment(created_comment["id"], payload)
        assert response.status_code == 200

    @allure.title("PUT /comments/{id} - todo updated after changing it")
    def test_update_comment_body_changed(
        self, api_client: MockApiClient, created_comment: dict
    ):
        payload = _comment_payload()
        response = api_client.update_comment(created_comment["id"], payload)
        assert api_client.data(response)["body"] == payload["body"]


@allure.suite("Comments API")
class TestPatchComment:
    @allure.title(
        "PATCH /comments/{id} - partial update (Expected to fail due to API bug)"
    )
    @pytest.mark.xfail(
        reason="Bug on apimocker.com: PATCH acts like PUT and requires all fields"
    )
    def test_patch_comment_partial_update(
        self, api_client: MockApiClient, created_comment: dict
    ):
        new_body = f"Patched comment body {uuid.uuid4().hex[:8]}"
        response = api_client.patch_comment(created_comment["id"], {"body": new_body})

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code} with body: {response.text}"

    @allure.title("PATCH /comments/{id} - works when all required fields are provided")
    def test_patch_comment_full_payload(
        self, api_client: MockApiClient, created_comment: dict
    ):
        new_body = f"Patched comment body {uuid.uuid4().hex[:8]}"

        payload = {
            "name": created_comment["name"],
            "email": created_comment["email"],
            "body": new_body,
            "postId": created_comment["postId"],
        }

        response = api_client.patch_comment(created_comment["id"], payload)

        if response.status_code == 404:
            pytest.xfail(
                "Bug on apimocker.com: PATCH returns 404 despite documentation"
            )

        assert response.status_code == 200
        assert api_client.data(response)["body"] == new_body
        assert api_client.data(response)["name"] == created_comment["name"]


@allure.suite("Comments API")
class TestDeleteComment:
    @allure.title("DELETE /comments/{id} - status 204")
    @pytest.mark.smoke
    def test_delete_comment_status(
        self, api_client: MockApiClient, created_comment: dict
    ):
        response = api_client.delete_comment(created_comment["id"])
        assert response.status_code == 204

    @allure.title("DELETE /comments/{id} - response body is empty")
    def test_delete_comment_empty_body(
        self, api_client: MockApiClient, created_comment: dict
    ):
        response = api_client.delete_comment(created_comment["id"])
        assert response.content == b""
