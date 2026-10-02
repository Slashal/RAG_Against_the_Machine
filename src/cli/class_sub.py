# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  class_sub.py                                      :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 18:27:37 by hguesne         #+#    #+#               #
#  Updated: 2026/10/02 18:03:34 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
"""Pydantic data models exchanged between the CLI pipeline stages."""

from typing import List
from pydantic import BaseModel


class MinimalSource(BaseModel):
    """A single retrieved source span from the indexed corpus."""

    file_path: str
    first_character_index: int
    last_character_index: int
    text: str


class MinimalSearchResults(BaseModel):
    """A single search result for one question."""

    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """A search result extended with a generated answer."""

    answer: str


class StudentSearchResults(BaseModel):
    """Dataset-level search output containing ranked sources."""

    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """Dataset-level answer output containing ranked sources and answers."""

    search_results: List[MinimalAnswer]
    k: int
