import requests
from typing import Any

from api.base_client import BaseClient
from api.endpoints import Endpoints
from core.allure_steps import api_step


class MockApiClient(BaseClient):
    """
    Client for apimocker.com.

    Each public method is a business scenario.
    Tests call these methods.
    """

    # USERS

    @api_step("GET /users — get all users")
    def get_users(self, params: dict | None = None) -> requests.Response:
        return self.get(Endpoints.USERS, params=params)

    @api_step("GET /users/{id} — get user by ID")
    def get_user(self, user_id: int | str) -> requests.Response:
        return self.get(Endpoints.user(user_id))

    @api_step("POST /users — create new user")
    def create_user(self, payload: dict[str, Any]) -> requests.Response:
        return self.post(Endpoints.USERS, json=payload)

    @api_step("PUT /users/{id} — update user by ID")
    def update_user(
        self, user_id: int | str, payload: dict[str, Any]
    ) -> requests.Response:
        return self.put(Endpoints.user(user_id), json=payload)

    @api_step("PATCH /users/{id} — partially update user by ID")
    def patch_user(
        self, user_id: int | str, payload: dict[str, Any]
    ) -> requests.Response:
        return self.patch(Endpoints.user(user_id), json=payload)

    @api_step("DELETE /users/{id} — remove user by ID")
    def delete_user(self, user_id: int | str) -> requests.Response:
        return self.delete(Endpoints.user(user_id))

    # POSTS

    @api_step("GET /posts — get all posts")
    def get_posts(self, params: dict | None = None) -> requests.Response:
        return self.get(Endpoints.POSTS, params=params)

    @api_step("GET /posts/{id} — get post by ID")
    def get_post(self, post_id: int | str) -> requests.Response:
        return self.get(Endpoints.post(post_id))

    @api_step("POST /posts — create new post")
    def create_post(self, payload: dict[str, Any]) -> requests.Response:
        return self.post(Endpoints.POSTS, json=payload)

    @api_step("PUT /posts/{id} — update post by ID")
    def update_post(
        self, post_id: int | str, payload: dict[str, Any]
    ) -> requests.Response:
        return self.put(Endpoints.post(post_id), json=payload)

    @api_step("PATCH /posts/{id} — partially update post by ID")
    def patch_post(
        self, post_id: int | str, payload: dict[str, Any]
    ) -> requests.Response:
        return self.patch(Endpoints.post(post_id), json=payload)

    @api_step("DELETE /posts/{id} — remove post by ID")
    def delete_post(self, post_id: int | str) -> requests.Response:
        return self.delete(Endpoints.post(post_id))

    # TODOS

    @api_step("GET /todos — get all todos")
    def get_todos(self, params: dict | None = None) -> requests.Response:
        return self.get(Endpoints.TODOS, params=params)

    @api_step("GET /todos/{id} — get todo by ID")
    def get_todo(self, todo_id: int | str) -> requests.Response:
        return self.get(Endpoints.todo(todo_id))

    @api_step("POST /todos — create new todo")
    def create_todo(self, payload: dict[str, Any]) -> requests.Response:
        return self.post(Endpoints.TODOS, json=payload)

    @api_step("PUT /todos/{id} — update todo by ID")
    def update_todo(
        self, todo_id: int | str, payload: dict[str, Any]
    ) -> requests.Response:
        return self.put(Endpoints.todo(todo_id), json=payload)

    @api_step("PATCH /todos/{id} — partially update todo by ID")
    def patch_todo(
        self, todo_id: int | str, payload: dict[str, Any]
    ) -> requests.Response:
        return self.patch(Endpoints.todo(todo_id), json=payload)

    @api_step("DELETE /todos/{id} — remove todo by ID")
    def delete_todo(self, todo_id: int | str) -> requests.Response:
        return self.delete(Endpoints.todo(todo_id))

    # COMMENTS

    @api_step("GET /comments — get all comments")
    def get_comments(self, params: dict | None = None) -> requests.Response:
        return self.get(Endpoints.COMMENTS, params=params)

    @api_step("GET /comments/{id} - get comment by ID")
    def get_comment(self, comment_id: int | str) -> requests.Response:
        return self.get((Endpoints.comment(comment_id)))

    @api_step("POST /comments — create new comment")
    def create_comment(self, payload: dict[str, Any]) -> requests.Response:
        return self.post(Endpoints.COMMENTS, json=payload)

    @api_step("PUT /comment/{id} - update comment by ID")
    def update_comment(
        self, comment_id: int | str, payload: dict[str, Any]
    ) -> requests.Response:
        return self.put(Endpoints.comment(comment_id), json=payload)

    @api_step("PATCH /comment/{id} - partially update comment by ID")
    def patch_comment(
        self, comment_id: int | str, payload: dict[str, Any]
    ) -> requests.Response:
        return self.patch(Endpoints.comment(comment_id), json=payload)

    @api_step("DELETE /comments/{id} — remove comment by ID")
    def delete_comment(self, comment_id: int | str) -> requests.Response:
        return self.delete(Endpoints.comment(comment_id))

    # ADVANCED FEATURES
    @api_step("GET /users/search — search users")
    def search_users(self, query: str) -> requests.Response:
        return self.get(f"{Endpoints.USERS}/search", params={"q": query})

    @api_step("GET /error/{code} — simulate error")
    def get_error(self, code: int | str) -> requests.Response:
        return self.get(f"/error/{code}")
