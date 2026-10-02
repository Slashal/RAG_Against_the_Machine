# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  cli.py                                            :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 14:05:45 by hguesne         #+#    #+#               #
#  Updated: 2026/10/02 16:51:43 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from typing import Optional
import fire
from src.cli.index import indexer
from src.cli.search import search
from src.cli.search_dataset import search_dataset
from src.cli.answer import answer
from src.cli.answer_dataset import answer_dataset
from src.cli.evaluate import evaluate


class CLI:
    def __init__(self) -> None:
        self.saveUA = "data/output/search_results/UnansweredQuestions"
        self.saveAQ = "data/output/search_results/AnsweredQuestions"

    def index(self, max_chunk_size: int = 2000,
              raw_path: str = "data/raw",
              processed_path: str = "data/processed") -> None:
        indexer(max_chunk_size, raw_path, processed_path)

    def search(self, query: str, k: int = 5,
               processed_path: str = "data/processed") -> None:
        search(query, k, processed_path)

    def search_dataset(self, dataset_path: str, k: int = 5,
                       save_directory: Optional[str] = None) -> None:
        if save_directory is None:
            save_directory = self.saveUA
        # Implementation for searching a dataset
        search_dataset(dataset_path, k, save_directory)

    def answer(self, question: str, k: int = 5) -> None:
        answer(question, k)

    def answer_dataset(self, student_search_results_path: str,
                       save_directory: Optional[str] = None) -> None:
        if save_directory is None:
            save_directory = self.saveAQ
        answer_dataset(student_search_results_path, save_directory)

    def evaluate(self, student_search_results_path: str,
                 dataset_path: str) -> None:
        evaluate(student_search_results_path, dataset_path)


def menu() -> None:

    fire.Fire(CLI())
