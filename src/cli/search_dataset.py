# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  search_dataset.py                                 :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 18:31:12 by hguesne         #+#    #+#               #
#  Updated: 2026/10/02 17:05:04 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Dataset search helpers that batch the single-query retrieval path."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tqdm import tqdm

from src.cli.class_sub import MinimalSearchResults, StudentSearchResults
from src.cli.search import search


def search_dataset(dataset_path: str, k: int = 5,
                   save_directory: str = "data/output/search_results") -> None:
    """Run search for every question in a dataset and save JSON output."""

    if not isinstance(dataset_path, str) or not dataset_path.strip():
        print("Warning: dataset_path is empty; skipping dataset search.")
        return
    if k <= 0:
        print("Warning: k must be > 0; skipping dataset search.")
        return

    input_path = Path(dataset_path)
    if not input_path.exists() or not input_path.is_file():
        print(f"Warning: dataset file not found: {dataset_path}")
        return

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            dataset_payload: Any = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Warning: malformed dataset JSON for {dataset_path}: {exc}")
        return

    if not isinstance(dataset_payload, dict):
        print(f"Warning: dataset JSON is not an object: {dataset_path}")
        return

    raw_dataset = dataset_payload.get("rag_questions")
    if not isinstance(raw_dataset, list):
        print(f"Warning: dataset has no 'rag_questions' list: {dataset_path}")
        return

    save_path = Path(save_directory) / input_path.name
    save_path.parent.mkdir(parents=True, exist_ok=True)

    results = StudentSearchResults(k=k, search_results=[])
    option = "[{elapsed}<{remaining}] {n_fmt}/{total_fmt} |"
    " {l_bar}{bar} {rate_fmt}{postfix}"

    for value in tqdm(raw_dataset, bar_format=option, colour='yellow',
                      desc="Dataset Search"):
        if not isinstance(value, dict):
            continue
        question = value.get("question")
        question_id = value.get("question_id")
        if not isinstance(question, str) or not question.strip():
            continue
        retrieved_sources = search(query=question, k=k, printable=0)
        results.search_results.append(
            MinimalSearchResults(
                question_id=(str(question_id) if question_id
                             is not None else ""),
                question=question,
                retrieved_sources=retrieved_sources,
            )
        )

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(results.model_dump(), f, indent=2)
