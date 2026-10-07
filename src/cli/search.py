# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  search.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 17:56:12 by hguesne         #+#    #+#               #
#  Updated: 2026/10/07 15:14:32 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Single-query retrieval over the persisted BM25 index."""

from __future__ import annotations
from pathlib import Path
from typing import Any, List
from src.cli.class_sub import MinimalSource
from src.cli.index import tokenize

import pickle


def search(query: str, k: int = 5,
           processed_path: str = "data/processed",
           printable: int = 1) -> List[MinimalSource]:
    """Return the top-k retrieved source spans for one query."""

    try:
        # S'il n'y a pas de question ou que la question n'est pas une str
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Invalid query: must be a non-empty string.")
        # Si k est inférieur ou égale a 0, n'est pas un int ou si > 10
        if k <= 0 or not isinstance(k, int) or k > 10:
            raise ValueError("Invalid value for k: must be 0 < k <= 10.")

        # Verifie que l'index pickle existe
        index_file = Path(processed_path) / "bm25_index.pkl"
        if not index_file.exists():
            raise ValueError("Index file not found.")
    except Exception as e:
        print(f"Error occurred while validating inputs: {e}")
        return []

    try:
        # Ouverture de l'index pickle
        with open(index_file, "rb") as f:
            data: Any = pickle.load(f)
        # Verification que la donnée chargée est bien un dictionnaire
        if not isinstance(data, dict):
            return []

        # Extraction du modèle BM25 et des chunks
        bm25_model = data.get("bm25")
        all_chunks = data.get("chunks")
        # Verification que les deux éléments sont présents dans le bon format
        if bm25_model is None or not isinstance(all_chunks, list):
            return []
        if not hasattr(bm25_model, "get_scores"):
            return []

        # Tokenisation de la question
        tokenized_query = tokenize(query)
        if not tokenized_query:
            return []

        # Récupération des scores bm25 pour les documents
        doc_scores = bm25_model.get_scores(tokenized_query)

        # Sélection des k meilleurs indices
        top_k_indices = sorted(
            range(len(doc_scores)),
            key=lambda i: float(doc_scores[i]), reverse=True,
        )[:k]

        # Récupération des résultats
        results: List[MinimalSource] = []
        for idx in top_k_indices:
            if idx < 0 or idx >= len(all_chunks):
                continue
            # Extraction du chunk correspondant
            res = all_chunks[idx]
            # Conversion du chunk en dictionnaire
            chunk = res.model_dump() if hasattr(res, "model_dump") else res
            if not isinstance(chunk, dict):
                continue
            # Si le paramètre printable est sur 1, print le résultat
            if printable:
                print(
                    f"{chunk['file_path']} [{chunk['first_character_index']}:"
                    f"{chunk['last_character_index']}]"
                )
            # Création d'une source minimale
            source = MinimalSource(
                file_path=str(chunk["file_path"]),
                first_character_index=int(chunk["first_character_index"]),
                last_character_index=int(chunk["last_character_index"]),
                text=str(chunk["text"]),
            )
            # Ajout de la source à la liste des résultats
            results.append(source)
        return results

    except (FileNotFoundError, OSError, ValueError,
            TypeError, pickle.PickleError):
        return []
