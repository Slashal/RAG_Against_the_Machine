# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  search.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 17:56:12 by hguesne         #+#    #+#               #
#  Updated: 2026/10/02 16:31:46 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from __future__ import annotations

from pathlib import Path
import pickle
from typing import Any, List

from rank_bm25 import BM25Plus

from src.cli.class_sub import MinimalSource
from src.cli.index import tokenize


def search(query: str, k: int = 5,
           processed_path: str = "data/processed",
           printable: int = 1) -> List[MinimalSource]:
    if not isinstance(query, str) or not query.strip():
        return []
    if k <= 0:
        return []

    index_file = Path(processed_path) / "bm25_index.pkl"
    if not index_file.exists():
        return []

    try:
        with open(index_file, "rb") as f:
            data: Any = pickle.load(f)
        if not isinstance(data, dict):
            return []
        bm25_model = data.get("bm25")
        all_chunks = data.get("chunks")
        if bm25_model is None or not isinstance(all_chunks, list):
            return []
        if not hasattr(bm25_model, "get_scores"):
            return []

        tokenized_query = tokenize(query)
        if not tokenized_query:
            return []

        doc_scores = bm25_model.get_scores(tokenized_query)
        top_k_indices = sorted(
            range(len(doc_scores)),
            key=lambda i: float(doc_scores[i]), reverse=True,
        )[:k]

        results: List[MinimalSource] = []
        for idx in top_k_indices:
            if idx < 0 or idx >= len(all_chunks):
                continue
            res = all_chunks[idx]
            chunk = res.model_dump() if hasattr(res, "model_dump") else res
            if not isinstance(chunk, dict):
                continue
            if printable:
                print(
                    f"{chunk['file_path']} [{chunk['first_character_index']}:"
                    f"{chunk['last_character_index']}]"
                )
            source = MinimalSource(
                file_path=str(chunk["file_path"]),
                first_character_index=int(chunk["first_character_index"]),
                last_character_index=int(chunk["last_character_index"]),
                text=str(chunk["text"]),
            )
            results.append(source)
        return results
    except (FileNotFoundError, OSError, ValueError, TypeError, pickle.PickleError):
        return []
