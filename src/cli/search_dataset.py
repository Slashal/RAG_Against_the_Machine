# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  search_dataset.py                                 :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 18:31:12 by hguesne         #+#    #+#               #
#  Updated: 2026/10/01 17:53:31 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import json
from src.cli.search import search
from src.cli.class_sub import MinimalSearchResults, StudentSearchResults
from tqdm import tqdm
from pathlib import Path

# class MinimalSource(BaseModel):
#     file_path: str
#     first_character_index: int
#     last_character_index: int
#     text: str


# class MinimalSearchResults(BaseModel):
#     question_id: str
#     question: str
#     retrieved_sources: List[MinimalSource]


# class StudentSearchResults(BaseModel):
#     search_results: List[MinimalSearchResults]
#     k: int


def search_dataset(dataset_path: str, k: int = 5,
                   save_directory: str = "data/output/search_results"):
    try:

        input_path = Path(dataset_path)
        file_name = input_path.name
        save_path = Path(save_directory) / file_name

        # Ensure the parent directory exists, NOT the file itself
        save_path.parent.mkdir(parents=True, exist_ok=True)
        results = StudentSearchResults(k=k, search_results=[])
        dataset = json.load(open(dataset_path, "r"))
        dataset = dataset["rag_questions"]
        option = "[{elapsed}<{remaining}] {n_fmt}/{total_fmt} |"
        " {l_bar}{bar} {rate_fmt}{postfix}"
        for value in tqdm(dataset, bar_format=option, colour='yellow',
                          desc="Dataset Search"):
            search_result = MinimalSearchResults(
                question_id=value['question_id'],
                question=value['question'],
                retrieved_sources=search(query=value['question'], k=k,
                                         printable=0)
            )
            results.search_results.append(search_result)
        with open(save_path, "w") as f:
            json.dump(results.model_dump(), f, indent=2)
    except Exception as e:
        print("Error occurred while searching dataset: " + str(e))
