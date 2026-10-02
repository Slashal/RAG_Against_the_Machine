# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  answer_dataset.py                                 :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 20:48:15 by hguesne         #+#    #+#               #
#  Updated: 2026/10/02 18:02:53 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
"""Batch answer generation for previously retrieved search results."""

import json
from pathlib import Path
from typing import List

from tqdm import tqdm

from src.cli.answer import generate_answer, load_llm
from src.cli.class_sub import MinimalAnswer
from src.cli.class_sub import StudentSearchResultsAndAnswer

# class StudentSearchResultsAndAnswer(BaseModel):
#     search_results: List[MinimalAnswer]
#     k: int

# class MinimalAnswer(MinimalSearchResults):
#     answer: str


def answer_dataset(student_search_results_path: str,
                   save_directory: str) -> None:
    """Generate answers for a search-results dataset
    and persist JSON output."""

    try:
        search_result: List[MinimalAnswer] = []
        with open(student_search_results_path, 'r') as f:
            dataset = json.load(f)
        tokenizer, model = load_llm()
        k = min(int(dataset['k']), 10)
        for data in tqdm(dataset['search_results'], desc="Generating answers"):
            question = data['question']
            context_source = []
            for source in data['retrieved_sources']:
                context_source.append(source['text'])
            answer = MinimalAnswer(answer=generate_answer(question,
                                                          context_source,
                                                          tokenizer,
                                                          model),
                                   **data)
            search_result.append(answer)
        result = StudentSearchResultsAndAnswer(search_results=search_result,
                                               k=k)
        output_directory = Path(save_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        with open(output_directory / "answer_dataset.json", 'w') as f:
            json.dump(result.model_dump(), f, indent=2)
    except Exception as e:
        print(f"Error occurred while processing the dataset: {e}")
