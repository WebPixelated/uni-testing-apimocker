import uuid
import pytest
import allure

from api.mock_api_client import MockApiClient
from helpers import random_name


def _post_payload() -> dict:
    uid = uuid.uuid4().hex[:8]
    return {
        "title": f"Test Post Title {uid}",
        "body": f"Test post body content {uid}",
    }


@allure.suite("Posts API")
class TestGetPosts:
    @allure.title("GET /posts - status 200")
    @pytest.mark.smoke
    def test_get_posts_status(self, api_client: MockApiClient):
        response = api_client.get_posts()
        assert response.status_code == 200

    @allure.title("GET /posts - body is a list")
    def test_get_posts_returns_list(self, api_client: MockApiClient):
        response = api_client.get_posts()
        assert isinstance(api_client.data(response), list)

    @allure.title("GET /posts - list is not empty")
    def test_get_posts_not_empty(self, api_client: MockApiClient):
        response = api_client.get_posts()
        assert len(api_client.data(response)) > 0

    @allure.title("GET /posts - has 'pagination' field")
    def test_get_posts_has_pagination(self, api_client: MockApiClient):
        response = api_client.get_posts()
        pagination = api_client.pagination(response)
        assert pagination is not None
        assert "total" in pagination
        assert "totalPages" in pagination

    @allure.title("GET /posts/{id} - status 200")
    @pytest.mark.smoke
    def test_get_post_by_id_status(self, api_client: MockApiClient):
        response = api_client.get_post(1)
        assert response.status_code == 200

    @allure.title("GET /posts/{id} - post has required fields")
    def test_get_post_has_required_fields(self, api_client: MockApiClient):
        post = api_client.data(api_client.get_post(1))
        for field in ("id", "title", "body", "userId"):
            assert field in post, f"Missing field: {field}"

    @allure.title("GET /posts/{id} - has inner 'user' object")
    def test_get_post_has_nested_user(self, api_client: MockApiClient):
        post = api_client.data(api_client.get_post(1))
        assert "user" in post
        assert "id" in post["user"]
        assert "name" in post["user"]
        assert "username" in post["user"]

    @allure.title("GET /posts/{id} - unavailable ID returns 404")
    def test_get_post_not_found(self, api_client: MockApiClient):
        response = api_client.get_post(99999)
        assert response.status_code == 404


@allure.suite("Posts API")
class TestCreatePost:
    @allure.title("POST /posts - status 201")
    @pytest.mark.smoke
    def test_create_post_status(self, api_client: MockApiClient):
        response = api_client.create_post(_post_payload())
        assert response.status_code == 201

    @allure.title("POST /posts - post has required fields")
    def test_create_post_returns_data(self, api_client: MockApiClient):
        payload = _post_payload()
        response = api_client.create_post(payload)
        post = api_client.data(response)
        assert post["title"] == payload["title"]
        assert post["body"] == payload["body"]

    @allure.title("POST /posts - response has ID")
    def test_create_post_has_id(self, api_client: MockApiClient):
        response = api_client.create_post(_post_payload())
        assert "id" in api_client.data(response)

    @allure.title("POST /posts - missing required fields")
    @pytest.mark.parametrize("missing_field", ["title", "body"])
    def test_create_post_missing_fields(
        self, api_client: MockApiClient, missing_field: str
    ):
        payload = _post_payload()
        payload.pop(missing_field)
        response = api_client.create_post(payload)
        assert response.status_code == 400
        assert any(
            d.get("path") == missing_field for d in response.json().get("details", [])
        )

    @allure.title("POST /posts - title exceeds max length (200 chars)")
    def test_create_post_title_too_long(self, api_client: MockApiClient):
        payload = _post_payload()
        payload["title"] = random_name(201)
        response = api_client.create_post(payload)
        assert response.status_code == 400

    @allure.title("POST /posts - body exceeds max length (5000 chars)")
    def test_create_post_body_too_long(self, api_client: MockApiClient):
        payload = _post_payload()
        payload["body"] = random_name(5001)
        response = api_client.create_post(payload)
        assert response.status_code == 400


@allure.suite("Posts API")
class TestUpdatePost:
    @allure.title("PUT /posts/{id} - status 200")
    def test_update_post_status(self, api_client: MockApiClient, created_post: dict):
        response = api_client.update_post(
            created_post["id"],
            {"title": f"Updated {uuid.uuid4().hex[:8]}", "body": "Updated body"},
        )
        assert response.status_code == 200

    @allure.title("PUT /posts/{id} - data updated")
    def test_update_post_data_changed(
        self, api_client: MockApiClient, created_post: dict
    ):
        new_title = f"Updated Title {uuid.uuid4().hex[:8]}"
        response = api_client.update_post(
            created_post["id"],
            {"title": new_title, "body": created_post["body"]},
        )
        assert api_client.data(response)["title"] == new_title


@allure.suite("Posts API")
class TestPatchPost:
    @allure.title(
        "PATCH /posts/{id} - partial update (Expected to fail due to API bug)"
    )
    @pytest.mark.xfail(
        reason="Bug on apimocker.com: PATCH acts like PUT and requires all fields"
    )
    def test_patch_post_partial_update(
        self, api_client: MockApiClient, created_post: dict
    ):
        new_title = f"Patched Title {uuid.uuid4().hex[:8]}"
        # Try to update title only
        response = api_client.patch_post(created_post["id"], {"title": new_title})

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code} with body: {response.text}"

    @allure.title("PATCH /posts/{id} - works when all required fields are provided")
    def test_patch_post_full_payload(
        self, api_client: MockApiClient, created_post: dict
    ):
        new_title = f"Patched Title {uuid.uuid4().hex[:8]}"
        payload = {"title": new_title, "body": created_post["body"]}
        response = api_client.patch_post(created_post["id"], payload)

        if response.status_code == 404:
            pytest.xfail(
                "Bug on apimocker.com: PATCH returns 404 despite documentation"
            )

        assert response.status_code == 200
        post = api_client.data(response)
        assert post["title"] == new_title
        assert post["body"] == created_post["body"]


@allure.suite("Posts API")
class TestDeletePost:
    @allure.title("DELETE /posts/{id} - status 204")
    @pytest.mark.smoke
    def test_delete_post_status(self, api_client: MockApiClient, created_post: dict):
        response = api_client.delete_post(created_post["id"])
        assert response.status_code == 204

    @allure.title("DELETE /posts/{id} - response body is empty")
    def test_delete_post_empty_body(
        self, api_client: MockApiClient, created_post: dict
    ):
        response = api_client.delete_post(created_post["id"])
        assert response.content == b""
