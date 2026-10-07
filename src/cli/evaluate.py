# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  evaluate.py                                       :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/30 17:42:18 by hguesne         #+#    #+#               #
#  Updated: 2026/10/07 15:22:18 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
"""Local recall@k evaluation helpers for the retrieval pipeline."""

from typing import Dict

import json


def is_valid(source: Dict[str, int], result: Dict[str, int]) -> bool:
    """Return whether two spans overlap enough to count as a match."""

    # Calcul le début du chevauchement entre les deux extraits
    first_overlap = max(source['first_character_index'],
                        result['first_character_index'])

    # Calcul la fin du chevauchement entre les deux extraits
    last_overlap = min(source['last_character_index'],
                       result['last_character_index'])

    # Calcul la taille du chevauchement
    overlap = max(0, last_overlap - first_overlap)

    # Calcul la longueur de la source
    source_length = (source['last_character_index'] -
                     source['first_character_index'])

    # Calcul la longueur du résultat
    result_length = (result['last_character_index'] -
                     result['first_character_index'])

    # Calcul la longueur de caractères qui ne sont pas partagés
    unique_char = source_length + result_length - overlap

    # Calcul l'intersection over union
    iou = (overlap / unique_char) if unique_char > 0 else 0

    return (iou >= 0.05)


def recallatk(source: list[Dict[str, int]],
              result: list[Dict[str, int]]) -> float:
    """Compute recall@k for one question from source and retrieved spans."""

    count = 0
    for s in source:
        for r in result:
            if is_valid(s, r):
                count += 1
                break

    return count / len(source) if source else 0.0


def evaluate(student_search_results_path: str, dataset_path: str) -> None:
    """Evaluate retrieval quality against a ground-truth dataset."""

    try:
        rak: float = 0.0

        # Chargement de dataset_path et student_search_results_path
        with open(student_search_results_path, 'r', encoding='utf-8') as f:
            student_data = json.load(f)
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset_data = json.load(f)

        # Parcourt les questions et les résultats de recherche
        # pour calculer le R@K (RecallAtK)
        for data, student_result in zip(dataset_data['rag_questions'],
                                        student_data['search_results']):
            source = data['sources']
            result = student_result['retrieved_sources']
            rak += recallatk(source, result)
        average_rak = round(rak / len(dataset_data['rag_questions']), 2)
        print(f"Average R@K: {average_rak}")

    except FileNotFoundError as exc:
        raise FileNotFoundError("File not found") from exc
    except json.JSONDecodeError as exc:
        raise ValueError("Error decoding JSON") from exc
