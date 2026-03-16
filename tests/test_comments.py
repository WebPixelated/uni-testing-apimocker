import uuid
import pytest
import allure

from api.mock_api_client import MockApiClient


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
