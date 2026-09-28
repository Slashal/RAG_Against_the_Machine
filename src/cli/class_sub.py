# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  class_sub.py                                      :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 18:27:37 by hguesne         #+#    #+#               #
#  Updated: 2026/09/28 18:34:39 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
from typing import List
from pydantic import BaseModel


class MinimalSource(BaseModel):
    file_path: str
    first_character_index: int
    last_character_index: int
    text: str


class MinimalSearchResults(BaseModel):
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    answer: str


class StudentSearchResults(BaseModel):
    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    search_results: List[MinimalAnswer]
    k: int
