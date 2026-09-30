# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  evaluate.py                                       :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/30 17:42:18 by hguesne         #+#    #+#               #
#  Updated: 2026/09/30 18:06:34 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
import json



def is_valid(source, result) -> bool:
    return source == result


def recallatk(source, result) -> float:
    count = 0
    for s in source:
        for r in result:
            if is_valid(s, r):
                count += 1
    return count / len(source) if source else 0.0


def evaluate(student_search_results_path: str, dataset_path: str):
    try:
        with open(student_search_results_path, 'r') as f:
            student_data = json.load(f)
        with open(dataset_path, 'r') as f:
            dataset_data = json.load(f)
        for data, student_result in zip(dataset_data['rag_questions'], student_data['search_results']):
            source = data['sources']
            result = student_result['retrieved_sources']
            recallatk(source, result)

    except FileNotFoundError:
        raise ("File not found")
    except json.JSONDecodeError:
        raise ("Error decoding JSON")