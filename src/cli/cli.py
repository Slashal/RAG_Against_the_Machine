# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  cli.py                                            :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 14:05:45 by hguesne         #+#    #+#               #
#  Updated: 2026/09/28 20:15:04 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from typing import Optional
import fire
from src.cli.index import indexer
from src.cli.search import search
from src.cli.search_dataset import search_dataset
from src.cli.answer import answer


class CLI:

    def index(self, max_chunk_size: Optional[int] = 2000,
              raw_path: str = "data/raw",
              processed_path: str = "data/processed") -> None:
        indexer(max_chunk_size, raw_path, processed_path)

    def search(self, query: str, k: int = 5,
               processed_path: str = "data/processed"):
        search(query, k, processed_path)

    def search_dataset(self, dataset_path: str, k: int = 5,
                       save_directory: str = "data/output/search_results"):
        # Implementation for searching a dataset
        search_dataset(dataset_path, k, save_directory)

    def answer(self, question: str, k: int = 5):
        answer(question, k)


def menu() -> str:

    fire.Fire(CLI())
