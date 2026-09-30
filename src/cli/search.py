# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  search.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 17:56:12 by hguesne         #+#    #+#               #
#  Updated: 2026/09/29 16:27:25 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from src.cli.class_sub import MinimalSource
from src.cli.index import tokenize
from typing import Dict, List
from pathlib import Path
import pickle
from rank_bm25 import BM25Okapi


def search(query: str, k: int = 5,
           processed_path: str = "data/processed",
           printable: int = 1) -> List[MinimalSource]:
    index_file = Path(processed_path) / "bm25_index.pkl"
    results = []
    if not index_file.exists():
        raise FileNotFoundError(f"L'index {index_file} n'existe pas."
                                " Exécutez d'abord la commande 'index'.")

    with open(index_file, "rb") as f:
        data = pickle.load(f)
        bm25_model: BM25Okapi = data["bm25"]
        all_chunks: List[Dict[str, object]] = data["chunks"]

    tokenized_query = tokenize(query)

    doc_scores = bm25_model.get_scores(tokenized_query)

    top_k_indices = sorted(range(len(doc_scores)),
                           key=lambda i: doc_scores[i], reverse=True)[:k]

    result = [all_chunks[i] for i in top_k_indices]

# Affichage terminal conforme aux attentes du sujet
    for res in result:
        if printable:
            print(f"{res['file_path']} [{res['first_character_index']}:" +
                  f"{res['last_character_index']}]")
        source = MinimalSource(
            file_path=str(res['file_path']),
            first_character_index=int(res['first_character_index']),
            last_character_index=int(res['last_character_index']),
            text=str(res['text'])
        )
        results.append(source)

    return results
