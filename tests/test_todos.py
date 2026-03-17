import uuid
import pytest
import allure

from api.mock_api_client import MockApiClient
from helpers import random_name


def _todo_payload() -> dict:
    return {"title": f"Test Todo {uuid.uuid4().hex[:8]}"}


@allure.suite("Todos API")
class TestGetTodos:
    @allure.title("GET /todos - status 200")
    @pytest.mark.smoke
    def test_get_todos_status(self, api_client: MockApiClient):
        response = api_client.get_todos()
        assert response.status_code == 200

    @allure.title("GET /todos - body is a list")
    def test_get_todos_returns_list(self, api_client: MockApiClient):
        response = api_client.get_todos()
        assert isinstance(api_client.data(response), list)

    @allure.title("GET /todos - list is not empty")
    def test_get_todos_not_empty(self, api_client: MockApiClient):
        response = api_client.get_todos()
        assert len(api_client.data(response)) > 0

    @allure.title("GET /todos - has 'pagination' field")
    def test_get_todos_has_pagination(self, api_client: MockApiClient):
        response = api_client.get_todos()
        pagination = api_client.pagination(response)
        assert pagination is not None
        assert "total" in pagination
        assert "totalPages" in pagination

    @allure.title("GET /todos/{id} - status 200")
    @pytest.mark.smoke
    def test_get_todo_by_id_status(self, api_client: MockApiClient):
        response = api_client.get_todo(1)
        assert response.status_code == 200

    @allure.title("GET /todos/{id} - todo has required fields")
    def test_get_todo_has_required_fields(self, api_client: MockApiClient):
        todo = api_client.data(api_client.get_todo(1))
        for field in ("id", "title", "completed", "userId"):
            assert field in todo, f"Missing field: {field}"

    @allure.title("GET /todos/{id} - 'completed' is a boolean type")
    def test_get_todo_completed_is_bool(self, api_client: MockApiClient):
        todo = api_client.data(api_client.get_todo(1))
        assert isinstance(todo["completed"], bool)

    @allure.title("GET /todos/{id} - has inner 'user' object")
    def test_get_todo_has_nested_user(self, api_client: MockApiClient):
        todo = api_client.data(api_client.get_todo(1))
        assert "user" in todo
        assert "id" in todo["user"]
        assert "name" in todo["user"]

    @allure.title("GET /todos/{id} - unavailable ID returns 404")
    def test_get_todo_not_found(self, api_client: MockApiClient):
        response = api_client.get_todo(99999)
        assert response.status_code == 404


@allure.suite("Todos API")
class TestCreateTodo:
    @allure.title("POST /todos - status 201")
    @pytest.mark.smoke
    def test_create_todo_status(self, api_client: MockApiClient):
        response = api_client.create_todo(_todo_payload())
        assert response.status_code == 201

    @allure.title("POST /todos - data has 'title' from payload")
    def test_create_todo_returns_data(self, api_client: MockApiClient):
        payload = _todo_payload()
        response = api_client.create_todo(payload)
        todo = api_client.data(response)
        assert todo["title"] == payload["title"]

    @allure.title("POST /todos - completed is defaulted to False")
    def test_create_todo_completed_default_false(self, api_client: MockApiClient):
        response = api_client.create_todo(_todo_payload())
        todo = api_client.data(response)
        assert todo["completed"] is False

    @allure.title("POST /todos - todo has ID")
    def test_create_todo_has_id(self, api_client: MockApiClient):
        response = api_client.create_todo(_todo_payload())
        assert "id" in api_client.data(response)

    @allure.title("POST /todos - missing title")
    def test_create_todo_missing_title(self, api_client: MockApiClient):
        response = api_client.create_todo({})
        assert response.status_code == 400
        assert any(d.get("path") == "title" for d in response.json().get("details", []))

    @allure.title("POST /todos - title exceeds max length (200 chars)")
    def test_create_todo_title_too_long(self, api_client: MockApiClient):
        payload = {"title": random_name(201)}
        response = api_client.create_todo(payload)
        assert response.status_code == 400


@allure.suite("Todos API")
class TestUpdateTodo:
    @allure.title("PUT /todos/{id} - status 200")
    def test_update_todo_status(self, api_client: MockApiClient, created_todo: dict):
        response = api_client.update_todo(
            created_todo["id"],
            {"title": f"Updated {uuid.uuid4().hex[:8]}", "completed": True},
        )
        assert response.status_code == 200

    @allure.title("PUT /todos/{id} - 'completed' field updated")
    def test_update_todo_completed_changed(
        self, api_client: MockApiClient, created_todo: dict
    ):
        response = api_client.update_todo(
            created_todo["id"],
            {"title": created_todo["title"], "completed": True},
        )
        assert api_client.data(response)["completed"] is True


@allure.suite("Todos API")
class TestPatchTodo:
    @allure.title(
        "PATCH /todos/{id} - partial update (Expected to fail due to API bug)"
    )
    @pytest.mark.xfail(
        reason="Bug on apimocker.com: PATCH acts like PUT and requires all fields"
    )
    def test_patch_todo_status(self, api_client: MockApiClient, created_todo: dict):
        response = api_client.patch_todo(created_todo["id"], {"completed": True})

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code} with body: {response.text}"
        )

        assert response.status_code == 200
        todo = api_client.data(response)
        assert todo["completed"] is True
        assert todo["title"] == created_todo["title"]

    @allure.title("PATCH /posts/{id} - works when all required fields are provided")
    def test_patch_todo_full_payload(
        self, api_client: MockApiClient, created_todo: dict
    ):
        new_title = f"Patched Title {uuid.uuid4().hex[:8]}"
        payload = {"title": new_title, "completed": created_todo["completed"]}
        response = api_client.patch_todo(created_todo["id"], payload)

        if response.status_code == 404:
            pytest.xfail(
                "Bug on apimocker.com: PATCH returns 404 despite documentation"
            )

        assert response.status_code == 200
        post = api_client.data(response)
        assert post["title"] == new_title
        assert post["completed"] == created_todo["completed"]


@allure.suite("Todos API")
class TestDeleteTodo:
    @allure.title("DELETE /todos/{id} - status 204")
    @pytest.mark.smoke
    def test_delete_todo_status(self, api_client: MockApiClient, created_todo: dict):
        response = api_client.delete_todo(created_todo["id"])
        assert response.status_code == 204

    @allure.title("DELETE /todos/{id} - response body is empty")
    def test_delete_todo_empty_body(
        self, api_client: MockApiClient, created_todo: dict
    ):
        response = api_client.delete_todo(created_todo["id"])
        assert response.content == b""
