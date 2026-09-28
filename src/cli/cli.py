# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  cli.py                                            :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 14:05:45 by hguesne         #+#    #+#               #
#  Updated: 2026/09/28 20:57:55 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from typing import Optional
import fire
from src.cli.index import indexer
from src.cli.search import search
from src.cli.search_dataset import search_dataset
from src.cli.answer import answer
from src.cli.answer_dataset import answer_dataset


class CLI:
    def __init__(self):
        self.saveUA = "data/output/search_results/UnansweredQuestions"
        self.saveAQ = "data/output/search_results/AnsweredQuestions"

    def index(self, max_chunk_size: Optional[int] = 2000,
              raw_path: str = "data/raw",
              processed_path: str = "data/processed") -> None:
        indexer(max_chunk_size, raw_path, processed_path)

    def search(self, query: str, k: int = 5,
               processed_path: str = "data/processed"):
        search(query, k, processed_path)

    def search_dataset(self, dataset_path: str, k: int = 5,
                       save_directory: Optional[str] = None):
        if save_directory is None:
            save_directory = self.saveUA
        # Implementation for searching a dataset
        search_dataset(dataset_path, k, save_directory)

    def answer(self, question: str, k: int = 5):
        answer(question, k)

    def answer_dataset(self, student_search_results_path: str,
                       save_directory: Optional[str] = None):
        if save_directory is None:
            save_directory = self.saveAQ
        answer_dataset(student_search_results_path, save_directory)
        pass


def menu() -> str:

    fire.Fire(CLI())
