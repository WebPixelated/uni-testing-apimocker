import requests
from typing import Any

from core.config import settings
from core.logger import logger
from core.allure_steps import attach_request, attach_response


class BaseClient:
    """
    An HTTP-client based on requests.Session.

    Each request is logged automatically:
        - logs with loguru
        - attaches to Allure-report
    """

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.base_url).rstrip("/")
        self.timeout = settings.request_timeout
        self._last_response: requests.Response | None = None

        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    # Internal

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _log_response(self, response: requests.Response) -> None:
        elapsed_ms = int(response.elapsed.total_seconds() * 1000)
        logger.info(
            f"{response.request.method} {response.url} ->"
            f"{response.status_code} ({elapsed_ms} ms)"
        )

    def _try_json(self, response: requests.Response) -> Any:
        try:
            return response.json()
        except Exception:
            return response.text

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json: Any = None,
        **kwargs,
    ) -> requests.Response:
        url = self._url(path)

        logger.debug(f"-> {method.upper()} {url} | params={params} | body={json}")
        attach_request(method, url, body=json)

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json,
            timeout=self.timeout,
            **kwargs,
        )

        self._last_response = response
        self._log_response(response)
        attach_response(response.status_code, self._try_json(response))

        return response

    # Response envelope helpers
    @staticmethod
    def data(response: requests.Response) -> Any:
        """Return 'data' field from response."""
        return response.json()["data"]

    @staticmethod
    def pagination(response: requests.Response) -> dict | None:
        """Returns 'pagination' field if exists."""
        return response.json().get("pagination")

    # Public HTTP methods
    def get(self, path: str, params: dict | None = None, **kwargs) -> requests.Response:
        return self._request("GET", path, params=params, **kwargs)

    def post(self, path: str, json: Any = None, **kwargs) -> requests.Response:
        return self._request("POST", path, json=json, **kwargs)

    def put(self, path: str, json: Any = None, **kwargs) -> requests.Response:
        return self._request("PUT", path, json=json, **kwargs)

    def patch(self, path: str, json: Any = None, **kwargs) -> requests.Response:
        return self._request("PATCH", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self._request("DELETE", path, **kwargs)

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()
