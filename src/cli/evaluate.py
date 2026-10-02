# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  evaluate.py                                       :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/30 17:42:18 by hguesne         #+#    #+#               #
#  Updated: 2026/10/02 17:05:04 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
"""Local recall@k evaluation helpers for the retrieval pipeline."""

import json
from typing import Dict


def is_valid(source: Dict[str, int], result: Dict[str, int]) -> bool:
    """Return whether two spans overlap enough to count as a match."""

    first_overlap = max(source['first_character_index'],
                        result['first_character_index'])
    last_overlap = min(source['last_character_index'],
                       result['last_character_index'])
    overlap = max(0, last_overlap - first_overlap)
    source_length = (source['last_character_index'] -
                     source['first_character_index'])
    result_length = (result['last_character_index'] -
                     result['first_character_index'])
    unique_char = source_length + result_length - overlap
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
        with open(student_search_results_path, 'r', encoding='utf-8') as f:
            student_data = json.load(f)
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset_data = json.load(f)
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
