# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  search_dataset.py                                 :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 18:31:12 by hguesne         #+#    #+#               #
#  Updated: 2026/10/07 16:05:13 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Dataset search helpers that batch the single-query retrieval path."""

from __future__ import annotations
from tqdm import tqdm
from pathlib import Path
from typing import Any
from src.cli.class_sub import AnsweredQuestion, MinimalSearchResults
from src.cli.class_sub import RagDataset, StudentSearchResults
from src.cli.class_sub import UnansweredQuestion
from src.cli.search import search

import json


def search_dataset(dataset_path: str, k: int = 5,
                   save_directory: str = None) -> None:
    """Run search for every question in a dataset and save JSON output."""

    try:
        # Validation des paramètres data_path et k
        if not isinstance(dataset_path, str) or not dataset_path.strip():
            raise ValueError("Warning: dataset_path is empty; "
                             "skipping dataset search.")
        if k <= 0 or k > 10 or not isinstance(k, int):
            raise ValueError("Warning: k must be 0 < k <= 10; skipping"
                             " dataset search.")

        # Vérification de l'existence de l'index
        input_path = Path(dataset_path)
        if not input_path.exists() or not input_path.is_file():
            raise FileNotFoundError("Warning: dataset file"
                                    f" not found: {dataset_path}")

    except Exception as e:
        raise ValueError(e)

    try:
        # Chargement du fichier JSON dataset
        with open(input_path, "r", encoding="utf-8") as f:
            dataset_payload: Any = json.load(f)
            raw_dataset = RagDataset.model_validate(dataset_payload)
            if not isinstance(dataset_payload, dict):
                raise ValueError("Warning: dataset JSON is not "
                                 f"an object: {dataset_path}")
            # Extraction des questions du dataset
            if not isinstance(raw_dataset, RagDataset):
                raise ValueError("Warning: dataset has no 'rag_questions'"
                                 f" list: {dataset_path}")

    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Warning: malformed dataset "
                         f"JSON for {dataset_path}: {exc}")

    # Création du répertoire de sauvegarde
    save_path = Path(save_directory) / input_path.name
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialisation des résultats
    results = StudentSearchResults(k=k, search_results=[])

    # Configuration de la barre de progression
    option = "[{elapsed}<{remaining}] {n_fmt}/{total_fmt} |"
    " {l_bar}{bar} {rate_fmt}{postfix}"

    for value in tqdm(raw_dataset.rag_questions, bar_format=option,
                      colour='yellow', desc="Dataset Search"):
        if (not isinstance(value, AnsweredQuestion) and
                not isinstance(value, UnansweredQuestion)):
            continue
        # Extraction de la question et de son ID
        print(value)
        question = value.question
        question_id = value.question_id

        # Récupération des sources correspondantes à la question
        retrieved_sources = search(query=question, k=k, printable=0)
        # Ajout des résultats à la liste des résultats
        results.search_results.append(
            MinimalSearchResults(
                question_id=(str(question_id) if question_id
                             is not None else ""),
                question=question,
                retrieved_sources=retrieved_sources,
            )
        )

    # Sauvegarde des résultats dans un fichier JSON
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(results.model_dump(), f, indent=2)
