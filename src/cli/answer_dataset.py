# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  answer_dataset.py                                 :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 20:48:15 by hguesne         #+#    #+#               #
#  Updated: 2026/09/28 21:58:37 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
import json
from src.cli.answer import generate_answer, load_llm
from src.cli.class_sub import StudentSearchResultsAndAnswer
from src.cli.class_sub import MinimalAnswer
from pathlib import Path
from typing import List
from tqdm import tqdm

# class StudentSearchResultsAndAnswer(BaseModel):
#     search_results: List[MinimalAnswer]
#     k: int

# class MinimalAnswer(MinimalSearchResults):
#     answer: str


def answer_dataset(student_search_results_path: str,
                   save_directory: str) -> None:
    try:
        search_result: List[MinimalAnswer] = []
        with open(student_search_results_path, 'r') as f:
            dataset = json.load(f)
        tokenizer, model = load_llm()
        k = dataset['k']
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
        # Save the results to a file
        Path(save_directory).mkdir(parents=True, exist_ok=True)
        with open(f"{save_directory}/answer_dataset.json", 'w') as f:
            json.dump(result.model_dump(), f, indent=2)
    except Exception as e:
        print(f"Error occurred while processing the dataset: {e}")
