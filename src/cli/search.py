# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  search.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 17:56:12 by hguesne         #+#    #+#               #
#  Updated: 2026/09/28 18:16:21 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from src.cli.index import tokenize
from typing import Dict, List
from pathlib import Path
import pickle
from rank_bm25 import BM25Okapi


def search(query: str, k: int = 5,
           processed_path: str = "data/processed") -> List[Dict[str, object]]:
    index_file = Path(processed_path) / "bm25_index.pkl"
    if not index_file.exists():
        raise FileNotFoundError(f"L'index {index_file} n'existe pas."
                                " Exécutez d'abord la commande 'index'.")

# 1. Charger l'index et les chunks sauvegardés
    with open(index_file, "rb") as f:
        data = pickle.load(f)
        bm25_model: BM25Okapi = data["bm25"]
        all_chunks: List[Dict[str, object]] = data["chunks"]

# 2. Tokeniser la requête de recherche
    tokenized_query = tokenize(query)

# 3. Calculer les scores BM25 pour chaque chunk
    doc_scores = bm25_model.get_scores(tokenized_query)

# 4. Récupérer les indices des k meilleurs scores (tri décroissant)
    top_k_indices = sorted(range(len(doc_scores)),
                           key=lambda i: doc_scores[i], reverse=True)[:k]

# 5. Formater les résultats au format MinimalSource
    results = [all_chunks[i] for i in top_k_indices]

# Affichage terminal conforme aux attentes du sujet
    for res in results:
        print(f"{res['file_path']} [{res['first_character_index']}:" +
              f"{res['last_character_index']}]")
    return results
