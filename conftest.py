import json
import uuid
import pytest
import allure
from typing import Generator

from api import MockApiClient
from core import settings, logger


def unique_email(prefix: str = "test") -> str:
    """Generates unique email for each test."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


def unique_username(prefix: str = "user") -> str:
    """Generates unique username for each test."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# Fixtures


@pytest.fixture(scope="session")
def api_client() -> Generator[MockApiClient, None, None]:
    """API Client for session."""
    client = MockApiClient(base_url=settings.base_url)
    logger.info(f"API client created -> base_url={settings.base_url}")
    yield client
    client.session.close()
    logger.info("API client session closed")


@pytest.fixture
def created_user(api_client) -> Generator[dict, None, None]:
    """Creates user before the test, removes after."""
    response = api_client.create_user(
        {
            "name": "Test User",
            "username": unique_username("testuser"),
            "email": unique_email("testuser"),
        }
    )
    user = api_client.data(response)
    logger.debug(f"Fixture: created user id={user.get('id')}")
    yield user
    api_client.delete_user(user["id"])
    logger.debug(f"Fixture: deleted user id={user.get('id')}")


@pytest.fixture
def created_post(api_client) -> Generator[dict, None, None]:
    """Creates post before the test, removes after."""
    response = api_client.create_post(
        {"title": "Test Post", "body": "Test post body content"}
    )
    post = api_client.data(response)
    logger.debug(f"Fixture: created post id={post.get('id')}")
    yield post
    api_client.delete_post(post["id"])
    logger.debug(f"Fixture: deleted post id={post.get('id')}")


@pytest.fixture
def created_todo(api_client) -> Generator[dict, None, None]:
    """Creates todo before the test, removes after."""
    response = api_client.create_todo({"title": "Test Todo"})
    todo = api_client.data(response)
    logger.debug(f"Fixture: created todo id={todo.get('id')}")
    yield todo
    api_client.delete_todo(todo["id"])
    logger.debug(f"Fixture: deleted todo id={todo.get('id')}")


@pytest.fixture
def created_comment(api_client) -> Generator[dict, None, None]:
    """Creates comment before the test, removes after."""
    response = api_client.create_comment(
        {
            "name": "Test user",
            "email": unique_email("commenter"),
            "body": "Test comment body",
            "postId": 1,
        }
    )
    comment = api_client.data(response)
    logger.debug(f"Fixture: created comment id={comment.get('id')}")
    yield comment
    api_client.delete_comment(comment["id"])
    logger.debug(f"Fixture: deleted comment id={comment.get('id')}")


# Allure attach on failure
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        logger.warning(f"Test FAILED: {item.nodeid}")

        # Attach last request/response if client is available
        client: MockApiClient | None = item.funcargs.get("api_client")
        if client and client._last_response is not None:
            resp = client._last_response
            body = _try_json(resp)
            allure.attach(
                json.dumps(
                    {
                        "method": resp.request.method,
                        "url": resp.url,
                        "status_code": resp.status_code,
                        "response_body": body,
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                name="Last request/response on failure",
                attachment_type=allure.attachment_type.JSON,
            )

            # Attach log file
            try:
                with open(settings.log_file, "r", encoding="utf-8") as f:
                    allure.attach(
                        f.read(),
                        name="loguru log",
                        attachment_type=allure.attachment_type.TEXT,
                    )
            except FileNotFoundError:
                pass


def _try_json(response):
    try:
        return response.json()
    except Exception:
        return response.text
