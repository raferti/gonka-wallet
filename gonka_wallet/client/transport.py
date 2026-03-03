"""Pure HTTP transport."""

import httpx


class HttpTransport:
    def __init__(self, timeout: int = 30):
        self._client = httpx.Client(timeout=timeout)

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def get(self, url: str, params: dict = None) -> dict:
        """HTTP GET, returns JSON."""
        try:
            response = self._client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise ConnectionError(f"HTTP GET failed: {e}") from e
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"HTTP GET failed with status {e.response.status_code}") from e

    def post(self, url: str, payload: dict) -> dict:
        """HTTP POST JSON, returns JSON."""
        try:
            response = self._client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise ConnectionError(f"HTTP POST failed: {e}") from e
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"HTTP POST failed with status {e.response.status_code}") from e

    def get_raw(self, url: str, params: dict = None) -> httpx.Response:
        """HTTP GET, returns raw Response (for non-200 handling)."""
        try:
            return self._client.get(url, params=params)
        except httpx.RequestError as e:
            raise ConnectionError(f"HTTP GET failed: {e}") from e
