from __future__ import annotations

from pathlib import Path

from src.cli.search import search
from src.cli.search_dataset import search_dataset


def test_search_handles_empty_and_zero_k() -> None:
    assert search("", k=0) == []
    assert search("   ", k=3) == []


def test_search_dataset_handles_missing_and_malformed_json(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    malformed = tmp_path / "bad.json"
    malformed.write_text("{not valid json", encoding="utf-8")

    try:
        search_dataset(str(missing), k=3, save_directory=str(tmp_path / "out"))
        search_dataset(str(malformed), k=3, save_directory=str(tmp_path / "out"))
    except Exception as exc:  # pragma: no cover - regression guard
        raise AssertionError(f"should not crash on invalid input: {exc}") from exc
