import functools
import json
from typing import Any, Callable

import allure
from core.logger import logger

# Attachment helpers


def attach_request(method: str, url: str, body: Any = None) -> None:
    content = {"method": method.upper(), "url": url}
    if body:
        content["body"] = body
    allure.attach(
        json.dumps(content, indent=2, ensure_ascii=False),
        name="Request",
        attachment_type=allure.attachment_type.JSON,
    )


def attach_response(status_code: int, body: Any) -> None:
    content = {"status_code": status_code, "body": body}
    allure.attach(
        json.dumps(content, indent=2, ensure_ascii=False),
        name="Response",
        attachment_type=allure.attachment_type.JSON,
    )


def attach_screenshot(screenshot_bytes: bytes, name: str = "screenshot") -> None:
    allure.attach(
        screenshot_bytes,
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


# Step decorator


def step(title: str) -> Callable:
    """
    Decorator that wraps a function in an allure.step and logs entry/exit.

    Usage:
        @step("Open login page")
        def open_login_page(self): ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"[STEP] {title}")
            with allure.step(title):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# API step decorator


def api_step(title: str) -> Callable:
    """
    Like @step, but also logs at INFO level — useful for HTTP calls.

    Usage:
        @api_step("GET /users — fetch all users")
        def get_users(self): ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"[API] {title}")
            with allure.step(title):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator
