# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  evaluate.py                                       :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/30 17:42:18 by hguesne         #+#    #+#               #
#  Updated: 2026/10/01 16:25:55 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
import json


def is_valid(source, result) -> bool:
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


def recallatk(source, result) -> float:
    count = 0
    for s in source:
        for r in result:
            if is_valid(s, r):
                count += 1
                break

    return count / len(source) if source else 0.0


def evaluate(student_search_results_path: str, dataset_path: str):
    try:
        rak = 0
        with open(student_search_results_path, 'r') as f:
            student_data = json.load(f)
        with open(dataset_path, 'r') as f:
            dataset_data = json.load(f)
        for data, student_result in zip(dataset_data['rag_questions'],
                                        student_data['search_results']):
            source = data['sources']
            result = student_result['retrieved_sources']
            rak += recallatk(source, result)
        print(f"R@K: {rak}")
        print(f"Average R@K: {rak / len(dataset_data['rag_questions']) if dataset_data['rag_questions'] else 0.0}")

    except FileNotFoundError:
        raise ("File not found")
    except json.JSONDecodeError:
        raise ("Error decoding JSON")
