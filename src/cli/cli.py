# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  cli.py                                            :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 14:05:45 by hguesne         #+#    #+#               #
#  Updated: 2026/10/07 16:04:13 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
"""Python Fire CLI entry point for indexing, retrieval, and evaluation."""

from src.cli.answer import answer
from src.cli.answer_dataset import answer_dataset
from src.cli.evaluate import evaluate
from src.cli.index import indexer
from src.cli.search import search
from src.cli.search_dataset import search_dataset
from src.api import serve

import fire


class CLI:
    """Expose project commands as Fire entry points."""

    # Définition des constantes maximales
    MAX_K = 10
    MAX_CHUNK_SIZE = 2000

    def index(self, max_chunk_size: int = 2000,
              raw_path: str = "data/raw",
              processed_path: str = "data/processed") -> None:
        """Build the BM25 index from the raw corpus."""

        max_chunk_size = min(max_chunk_size, self.MAX_CHUNK_SIZE)
        indexer(max_chunk_size, raw_path, processed_path)

    def search(self, query: str, k: int = 5,
               processed_path: str = "data/processed") -> None:
        """Return the top-k sources for a single query."""

        k = min(k, self.MAX_K)
        search(query, k, processed_path)

    def search_dataset(self, dataset_path: str, k: int = 5,
                       save_directory: str = None) -> None:
        """Run search over a dataset and save StudentSearchResults JSON."""

        k = min(k, self.MAX_K)
        search_dataset(dataset_path, k, save_directory)

    def answer(self, question: str, k: int = 5) -> None:
        """Generate one grounded answer for a single question."""

        k = min(k, self.MAX_K)
        print(answer(question, k))

    def answer_dataset(self, student_search_results_path: str,
                       save_directory: str = None) -> None:
        """Generate answers for a dataset and save
        StudentSearchResultsAndAnswer JSON."""

        answer_dataset(student_search_results_path, save_directory)

    def evaluate(self, student_search_results_path: str,
                 dataset_path: str) -> None:
        """Compute the local recall@k score against a reference dataset."""

        evaluate(student_search_results_path, dataset_path)

    def serve(self, host: str = "127.0.0.1", port: int = 8080,
              processed_path: str = "data/processed",
              default_k: int = 5) -> None:
        """Start the local HTTP API for search and answer requests."""

        default_k = min(default_k, self.MAX_K)
        serve(host, port, processed_path, default_k)


def menu() -> None:
    """Run the CLI with Python Fire."""

    fire.Fire(CLI())
