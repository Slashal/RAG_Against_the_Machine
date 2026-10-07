"""Small local HTTP API for search and answer requests."""

from __future__ import annotations
from src.cli.answer import answer
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, cast
from urllib.parse import urlparse
from src.cli.search import search

import json


@dataclass(frozen=True)
class APIServerConfig:
    """Configuration for the local HTTP API server."""

    host: str = "127.0.0.1"
    port: int = 8080
    processed_path: str = "data/processed"
    default_k: int = 5


class RAGHTTPServer(ThreadingHTTPServer):
    """HTTP server carrying the API configuration."""

    config: APIServerConfig


def _json_response(payload: dict[str, Any],
                   status: int = 200) -> tuple[int, bytes]:
    """Serialize a JSON response payload."""

    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    return status, body


class _RAGRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler exposing search and answer endpoints."""

    server_version = "RAGHTTP/1.0"

    def _config(self) -> APIServerConfig:
        """Get the API server configuration.
        """
        server = cast(RAGHTTPServer, self.server)
        return server.config

    def _read_json(self) -> dict[str, Any]:
        """Read and parse the JSON body of the request."""

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = (self.rfile.read(content_length) if
                    content_length > 0 else b"{}")
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("invalid JSON body") from exc
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        """ Send a JSON response."""

        response_status, response_body = _json_response(payload, status)
        self.send_response(response_status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def do_GET(self) -> None:  # noqa: N802
        """Serve a simple health endpoint."""

        path = urlparse(self.path).path
        if path == "/health":
            self._send_json({"status": "ok"})
            return
        self._send_json({"error": "not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        """Serve search and answer endpoints."""

        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            query = payload.get("query")
            k_value = payload.get("k", self._config().default_k)
            if not isinstance(query, str) or not query.strip():
                raise ValueError("'query' must be a non-empty string")
            if not isinstance(k_value, int):
                raise ValueError("'k' must be an integer")
            if k_value <= 0:
                raise ValueError("'k' must be greater than zero")

            if path == "/search":
                results = search(query, k_value,
                                 self._config().processed_path, printable=0)
                self._send_json({
                    "query": query,
                    "k": k_value,
                    "search_results": [item.model_dump() for item in results],
                })
                return

            if path == "/answer":
                results = search(query, k_value,
                                 self._config().processed_path, printable=0)
                response = {
                    "query": query,
                    "k": k_value,
                    "answer": answer(query, self._config().processed_path,
                                     k_value),
                    "retrieved_sources": [item.model_dump()
                                          for item in results],
                }
                self._send_json(response)
                return

            self._send_json({"error": "not found"}, status=404)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - defensive HTTP guard
            self._send_json({"error": f"internal server error: {exc}"},
                            status=500)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        """Keep the server output quiet and CLI-friendly."""
        pass


def serve(host: str = "127.0.0.1", port: int = 8080,
          processed_path: str = "data/processed",
          default_k: int = 5) -> None:
    """Run the local HTTP API server."""

    default_k = min(default_k, 10)
    config = APIServerConfig(
        host=host,
        port=port,
        processed_path=processed_path,
        default_k=default_k,
    )
    server = RAGHTTPServer((config.host, config.port), _RAGRequestHandler)
    server.config = config
    print(f"Serving RAG API on http://{config.host}:{config.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down API server...")
    finally:
        server.server_close()
