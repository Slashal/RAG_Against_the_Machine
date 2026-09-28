# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  cli.py                                            :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 14:05:45 by hguesne         #+#    #+#               #
#  Updated: 2026/09/28 17:43:47 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from typing import Optional
import fire
from src.cli.index import indexer


class CLI:

    def index(self, max_chunk_size: Optional[int] = 2000,
              raw_path: str = "data/raw",
              processed_path: str = "data/processed") -> None:
        indexer(max_chunk_size, raw_path, processed_path)

    def search(self):
        pass


def menu() -> str:

    fire.Fire(CLI())
