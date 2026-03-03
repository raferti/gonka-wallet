from unittest.mock import patch, MagicMock

import httpx
import pytest

from gonka_wallet.client.transport import HttpTransport


@pytest.fixture
def mock_httpx_client():
    with patch("gonka_wallet.client.transport.httpx.Client") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def transport(mock_httpx_client):
    return HttpTransport(timeout=10)


class TestGet:
    def test_returns_json(self, transport, mock_httpx_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.get.return_value = mock_response

        result = transport.get("http://example.com/api")
        assert result == {"key": "value"}
        mock_httpx_client.get.assert_called_once_with("http://example.com/api", params=None)

    def test_network_error(self, transport, mock_httpx_client):
        mock_httpx_client.get.side_effect = httpx.ConnectError("connection refused")
        with pytest.raises(ConnectionError):
            transport.get("http://example.com/api")

    def test_http_500(self, transport, mock_httpx_client):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        )
        mock_httpx_client.get.return_value = mock_response

        with pytest.raises(ConnectionError, match="500"):
            transport.get("http://example.com/api")


class TestPost:
    def test_sends_json(self, transport, mock_httpx_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "ok"}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = transport.post("http://example.com/api", {"data": 1})
        assert result == {"result": "ok"}
        mock_httpx_client.post.assert_called_once_with("http://example.com/api", json={"data": 1})


class TestGetRaw:
    def test_returns_response(self, transport, mock_httpx_client):
        mock_response = MagicMock(spec=httpx.Response)
        mock_httpx_client.get.return_value = mock_response

        result = transport.get_raw("http://example.com/api")
        assert result is mock_response


class TestClose:
    def test_closes_client(self, transport, mock_httpx_client):
        transport.close()
        mock_httpx_client.close.assert_called_once()


class TestContextManager:
    def test_works(self, mock_httpx_client):
        with HttpTransport(timeout=10) as t:
            assert t is not None
        mock_httpx_client.close.assert_called_once()
